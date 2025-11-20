"""
Реализация TranscriptionService с использованием Borealis модели.
Обрабатывает аудио файлы и возвращает транскрипцию текста.

Production v4.0 (FULLY OPTIMIZED)
✅ Batch Size 32 (оптимальный для RTX 5080)
✅ Pinned Memory для быстрого копирования CPU→GPU
✅ Асинхронная обработка GPU/CPU
✅ CUDA Streams и non-blocking transfer
✅ Умное разрезание по паузам (контекст сохранен)
"""

import os
import sys
import time
import tempfile
import threading
from pathlib import Path
from queue import Queue

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Отключаем онлайн-загрузку моделей
os.environ['HF_HUB_OFFLINE'] = '1'

from generated.v1 import transcription_pb2
from generated.v1 import transcription_pb2_grpc
from services.transcription.base_service import TranscriptionServiceBase
from resources.config import config

import torch
import librosa
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoFeatureExtractor


class BorealisTranscriptionService(TranscriptionServiceBase, transcription_pb2_grpc.TranscriptionServiceServicer):
    """
    Реализация TranscriptionService с использованием Borealis ML модели.
    Принимает аудио файлы и возвращает транскрипцию с использованием модели Borealis (Vikhrmodels/Borealis).

    Оптимизации v4.0:
    - Batch Size 32 для максимальной производительности
    - Pinned Memory для быстрого DMA копирования
    - Асинхронная обработка GPU/CPU
    - CUDA Streams для параллельной работы
    - Умное разрезание аудио по паузам
    """

    def __init__(self):
        """Инициализация Borealis сервиса транскрипции"""
        super().__init__()

        self.logger.info("=" * 80)
        self.logger.info("BorealisTranscriptionService - Production v4.0 (FULLY OPTIMIZED)")
        self.logger.info("=" * 80)

        # Загрузка конфигурации
        self.logger.info("Загрузка конфигурации...")
        self.logger.info(f"  MODEL_NAME: {config.MODEL_NAME}")
        self.logger.info(f"  DEVICE: {config.DEVICE}")
        self.logger.info(f"  BATCH_SIZE: {config.BATCH_SIZE}")
        self.logger.info(f"  TARGET_CHUNK_DURATION: {config.TARGET_CHUNK_DURATION}s")
        self.logger.info(f"  LOCAL_FILES_ONLY: {config.MODEL_LOCAL_FILES_ONLY}")

        # Загрузка модели Borealis
        self.logger.info("Загрузка модели Borealis...")

        self.model = AutoModelForCausalLM.from_pretrained(
            config.MODEL_NAME,
            trust_remote_code=True,
            local_files_only=config.MODEL_LOCAL_FILES_ONLY
        )
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME, local_files_only=config.MODEL_LOCAL_FILES_ONLY)
        self.extractor = AutoFeatureExtractor.from_pretrained(config.MODEL_NAME, local_files_only=config.MODEL_LOCAL_FILES_ONLY)

        self.model.eval()
        self.model.to(config.DEVICE)
        self.model = torch.compile(self.model, mode="reduce-overhead", fullgraph=False)

        self.logger.info(f"✓ Модель загружена на {next(self.model.parameters()).device}")

        # CUDA streams
        self.compute_stream = torch.cuda.default_stream()
        self.transfer_stream = torch.cuda.Stream()

        # Параметры генерации
        self.generation_params = {
            "max_new_tokens": 350,
            "do_sample": True,
            "top_p": 0.9,
            "top_k": 50,
            "temperature": 0.2,
            "use_cache": True,
        }

        self.logger.info("✓ BorealisTranscriptionService инициализирован")
        self.logger.info("=" * 80)

    def _find_optimal_cut_points(self, waveform, sr, target_chunk_duration=None, window_duration=5):
        """Находит оптимальные точки разрезания по энергии"""
        if target_chunk_duration is None:
            target_chunk_duration = config.TARGET_CHUNK_DURATION

        self.logger.info("Анализ: поиск оптимальных точек разрезания...")

        frame_length = 2048
        hop_length = 512

        S = librosa.stft(waveform, n_fft=frame_length, hop_length=hop_length)
        magnitude = np.abs(S)
        energy = np.sum(magnitude ** 2, axis=0)
        energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-10)

        def frame_to_time(frame_idx):
            return (frame_idx * hop_length) / sr

        def time_to_frame(time_s):
            return int((time_s * sr) / hop_length)

        total_duration = len(waveform) / sr
        cut_points = []

        for i in range(1, int(total_duration / target_chunk_duration) + 1):
            target_time = i * target_chunk_duration
            if target_time >= total_duration:
                break

            window_frames = int((window_duration * sr) / hop_length)
            target_frame = time_to_frame(target_time)
            start_frame = max(0, target_frame - window_frames // 2)
            end_frame = min(len(energy), target_frame + window_frames // 2)

            window_energy = energy[start_frame:end_frame]
            min_energy_idx = np.argmin(window_energy)
            best_frame = start_frame + min_energy_idx
            best_time = frame_to_time(best_frame)

            cut_points.append(best_time)

        self.logger.info(f"✓ Найдено {len(cut_points)} точек разрезания")
        return cut_points

    def _split_audio_by_cut_points(self, waveform, sr, cut_points):
        """Разбивает аудио по точкам"""
        chunks = []
        prev_pos = 0

        for best_time in cut_points:
            cut_sample = int(best_time * sr)
            chunk = waveform[prev_pos:cut_sample]
            if len(chunk) > 0:
                chunks.append(chunk)
            prev_pos = cut_sample

        if prev_pos < len(waveform):
            chunks.append(waveform[prev_pos:])

        return chunks

    def _prepare_batch_pinned(self, chunks, start_idx, batch_size, sr):
        """
        Подготавливает батч в Pinned Memory
        Это позволяет DMA копирование (быстрее с CPU на GPU)
        """
        batch = chunks[start_idx:start_idx+batch_size]

        mel_batch = []
        att_mask_batch = []

        for chunk in batch:
            proc = self.extractor(chunk, sampling_rate=sr, padding="max_length",
                                 max_length=480_000, return_attention_mask=True, return_tensors="pt")
            mel_batch.append(proc.input_features.squeeze(0))
            att_mask_batch.append(proc.attention_mask.squeeze(0))

        mel = torch.stack(mel_batch)
        att_mask = torch.stack(att_mask_batch)

        # ✅ Зафиксируем в Pinned Memory
        mel = mel.pin_memory()
        att_mask = att_mask.pin_memory()

        return mel, att_mask

    def _process_chunks_v4(self, chunks, sr, batch_size=None):
        """
        Оптимизированная асинхронная обработка v4.0

        ✅ Batch Size из конфигурации
        ✅ Pinned Memory
        ✅ Асинхронное копирование
        ✅ GPU + CPU параллельно
        """
        if batch_size is None:
            batch_size = config.BATCH_SIZE

        results = []
        results_lock = threading.Lock()
        batch_queue = Queue(maxsize=2)
        stop_event = threading.Event()

        def gpu_worker():
            """Поток обработки GPU"""
            try:
                while not stop_event.is_set():
                    try:
                        item = batch_queue.get(timeout=1)
                        if item is None:
                            break

                        mel, att_mask, batch_indices = item

                        # Асинхронное копирование в отдельном stream
                        with torch.cuda.stream(self.transfer_stream):
                            mel = mel.to("cuda", non_blocking=True)
                            att_mask = att_mask.to("cuda", non_blocking=True)

                        # Синхронизируем
                        self.transfer_stream.synchronize()

                        # Обработка на GPU
                        with torch.inference_mode():
                            transcripts = self.model.generate(
                                mel=mel, att_mask=att_mask,
                                **self.generation_params
                            )

                        with results_lock:
                            for idx, transcript in zip(batch_indices, transcripts):
                                results.append((idx, str(transcript)))

                    except Exception as e:
                        self.logger.error(f"GPU worker ошибка: {e}")
            except Exception as e:
                self.logger.error(f"GPU worker fatal: {e}")

        # Запускаем GPU поток
        gpu_thread = threading.Thread(target=gpu_worker, daemon=False)
        gpu_thread.start()

        # ========== MAIN LOOP (CPU) ==========
        self.logger.info(f"Обработка: v4.0 - Асинхронная обработка {len(chunks)} кусков")
        self.logger.info(f"           Batch Size: {batch_size} | Pinned Memory ✓ | GPU + CPU параллельно ⚡")

        for batch_start_idx in range(0, len(chunks), batch_size):
            # CPU подготавливает батч пока GPU работает
            mel, att_mask = self._prepare_batch_pinned(chunks, batch_start_idx, batch_size, sr)
            batch_indices = list(range(batch_start_idx, min(batch_start_idx + batch_size, len(chunks))))

            # Отправляем в очередь
            batch_queue.put((mel, att_mask, batch_indices))

            # Прогресс
            processed = min(batch_start_idx + batch_size, len(chunks))
            progress = (processed / len(chunks)) * 100
            self.logger.info(f"  Прогресс: {processed}/{len(chunks)} ({progress:.0f}%)")

        # Завершение
        batch_queue.put(None)
        gpu_thread.join()

        # Сортируем результаты в правильном порядке
        results.sort(key=lambda x: x[0])
        return [text for _, text in results]

    def _transcribe_audio_file(self, audio_path):
        """
        Полная обработка аудио файла с использованием Borealis модели

        Args:
            audio_path: Путь к аудио файлу

        Returns:
            Транскрипция текста
        """
        transcription_start = time.time()

        # Загрузка аудио
        self.logger.info(f"Загрузка аудио: {audio_path}")
        load_start = time.time()

        waveform, sr = librosa.load(audio_path, sr=16_000)
        total_duration = len(waveform) / sr
        load_time = time.time() - load_start

        self.logger.info(f"✓ Загружено {total_duration:.1f}s за {load_time:.2f}s")

        # Анализ и разрезание
        analysis_start = time.time()
        cut_points = self._find_optimal_cut_points(waveform, sr)
        chunks = self._split_audio_by_cut_points(waveform, sr, cut_points)
        analysis_time = time.time() - analysis_start

        self.logger.info(f"✓ Разбито на {len(chunks)} кусков за {analysis_time:.2f}s")

        # Обработка
        process_start = time.time()
        results = self._process_chunks_v4(chunks, sr)
        process_time = time.time() - process_start

        full_transcript = " ".join(results)

        self.logger.info(f"✓ Обработано за {process_time:.2f}s")
        self.logger.info(f"  Скорость: {total_duration/process_time:.1f}x от реального времени")

        # Статистика
        total_time = time.time() - transcription_start
        words = len(full_transcript.split())
        chars = len(full_transcript)
        gpu_mem = torch.cuda.memory_allocated() / 1e9

        self.logger.info("=" * 80)
        self.logger.info("РЕЗУЛЬТАТ v4.0 FULLY OPTIMIZED")
        self.logger.info("=" * 80)
        self.logger.info(f"⏱️  Время: Загрузка={load_time:.2f}s | Анализ={analysis_time:.2f}s | Транскрипция={process_time:.2f}s | ИТОГО={total_time:.2f}s")
        self.logger.info(f"📊 Текст: Символов={chars} | Слов={words} | Скорость={total_duration/total_time:.1f}x")
        self.logger.info(f"💾 GPU: Использовано={gpu_mem:.2f}GB")
        self.logger.info("=" * 80)

        return full_transcript

    def TranscribeAudio(self, request, context):
        """
        Принимает аудио файл и возвращает транскрипцию.

        Args:
            request: AudioRequest с данными аудио файла
            context: gRPC context

        Returns:
            TranscriptionResponse с результатом транскрипции
        """
        start_time = time.time()

        self.logger.info("=" * 80)
        self.logger.info(f"📥 Получен запрос на транскрипцию файла: {request.filename}")
        self.logger.info(f"   Размер файла: {len(request.audio_data) / (1024*1024):.2f} МБ")
        self.logger.info(f"   Формат: {request.format}")
        self.logger.info("=" * 80)

        # Валидация запроса
        is_valid, error_msg = self._validate_transcription_request(request.filename, request.audio_data)

        if not is_valid:
            self.logger.error(f"❌ Ошибка валидации: {error_msg}")
            processing_time = time.time() - start_time

            return transcription_pb2.TranscriptionResponse(
                transcript="",
                success=False,
                error_message=error_msg,
                processing_time=processing_time,
                audio_duration=0.0,
                stats=transcription_pb2.TranscriptionStats(
                    word_count=0,
                    char_count=0,
                    speed_factor=0.0
                )
            )

        # Транскрипция с использованием Borealis модели
        try:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=f".{request.format}", delete=False) as temp_file:
                temp_file.write(request.audio_data)
                temp_audio_path = temp_file.name

            self.logger.info(f"💾 Временный файл создан: {temp_audio_path}")

            # Запускаем транскрипцию с использованием интегрированной логики
            transcript = self._transcribe_audio_file(temp_audio_path)

            # Вычисляем длительность для статистики
            waveform, sr = librosa.load(temp_audio_path, sr=16_000)
            audio_duration = len(waveform) / sr

            # Удаляем временный файл
            try:
                Path(temp_audio_path).unlink()
                self.logger.info(f"🗑️  Временный файл удален")
            except Exception as e:
                self.logger.warning(f"⚠️  Не удалось удалить временный файл: {e}")

            if transcript is None or transcript == "":
                raise Exception("Транскрипция вернула пустой результат")

            processing_time = time.time() - start_time
            word_count = len(transcript.split())
            char_count = len(transcript)
            speed_factor = audio_duration / processing_time if processing_time > 0 else 0.0

            self.logger.info("=" * 80)
            self.logger.info(f"✅ Транскрипция успешно завершена!")
            self.logger.info(f"   Общее время обработки: {processing_time:.2f} сек")
            self.logger.info(f"   Скорость: {speed_factor:.1f}x от реального времени")
            self.logger.info(f"   Слов: {word_count}, Символов: {char_count}")
            self.logger.info("=" * 80)

            return transcription_pb2.TranscriptionResponse(
                transcript=transcript,
                success=True,
                error_message="",
                processing_time=processing_time,
                audio_duration=audio_duration,
                stats=transcription_pb2.TranscriptionStats(
                    word_count=word_count,
                    char_count=char_count,
                    speed_factor=speed_factor
                )
            )

        except Exception as e:
            error_msg = f"Ошибка при транскрипции: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            processing_time = time.time() - start_time

            # Пытаемся удалить временный файл в случае ошибки
            try:
                if 'temp_audio_path' in locals():
                    Path(temp_audio_path).unlink()
            except:
                pass

            return transcription_pb2.TranscriptionResponse(
                transcript="",
                success=False,
                error_message=error_msg,
                processing_time=processing_time,
                audio_duration=0.0,
                stats=transcription_pb2.TranscriptionStats(
                    word_count=0,
                    char_count=0,
                    speed_factor=0.0
                )
            )

    def TranscribeAudioStream(self, request_iterator, context):
        """
        Принимает аудио файл через стрим и возвращает транскрипцию.

        Args:
            request_iterator: Итератор AudioChunk
            context: gRPC context

        Returns:
            TranscriptionResponse с результатом транскрипции
        """
        start_time = time.time()

        self.logger.info("=" * 80)
        self.logger.info("📥 Получен стриминговый запрос на транскрипцию")
        self.logger.info("=" * 80)

        filename = ""
        format_type = ""
        sample_rate = 0
        chunks_data = []
        chunk_count = 0

        try:
            for chunk in request_iterator:
                chunk_count += 1

                # Первый чанк содержит метаданные
                if chunk_count == 1:
                    filename = chunk.filename
                    format_type = chunk.format
                    sample_rate = chunk.sample_rate
                    self.logger.info(f"📂 Начало приема файла: {filename}")

                # Собираем данные
                chunks_data.append(chunk.chunk_data)

            # Объединяем все чанки
            audio_data = b''.join(chunks_data)
            actual_size = len(audio_data)

            self.logger.info(f"✓ Получено {chunk_count} чанков, всего {actual_size / (1024*1024):.2f} МБ")

            # Валидация
            is_valid, error_msg = self._validate_transcription_request(filename, audio_data)

            if not is_valid:
                self.logger.error(f"❌ Ошибка валидации: {error_msg}")
                processing_time = time.time() - start_time

                return transcription_pb2.TranscriptionResponse(
                    transcript="",
                    success=False,
                    error_message=error_msg,
                    processing_time=processing_time,
                    audio_duration=0.0,
                    stats=transcription_pb2.TranscriptionStats(
                        word_count=0,
                        char_count=0,
                        speed_factor=0.0
                    )
                )

            # Транскрипция с использованием Borealis модели
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=f".{format_type}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name

            self.logger.info(f"💾 Временный файл создан: {temp_audio_path}")

            # Запускаем транскрипцию с использованием интегрированной логики
            transcript = self._transcribe_audio_file(temp_audio_path)

            # Вычисляем длительность для статистики
            waveform, sr = librosa.load(temp_audio_path, sr=16_000)
            audio_duration = len(waveform) / sr

            # Удаляем временный файл
            try:
                Path(temp_audio_path).unlink()
                self.logger.info(f"🗑️  Временный файл удален")
            except Exception as e:
                self.logger.warning(f"⚠️  Не удалось удалить временный файл: {e}")

            if transcript is None or transcript == "":
                raise Exception("Транскрипция вернула пустой результат")

            processing_time = time.time() - start_time
            word_count = len(transcript.split())
            char_count = len(transcript)
            speed_factor = audio_duration / processing_time if processing_time > 0 else 0.0

            self.logger.info("=" * 80)
            self.logger.info(f"✅ Стриминговая транскрипция успешно завершена!")
            self.logger.info(f"   Общее время обработки: {processing_time:.2f} сек")
            self.logger.info(f"   Скорость: {speed_factor:.1f}x от реального времени")
            self.logger.info(f"   Слов: {word_count}, Символов: {char_count}")
            self.logger.info("=" * 80)

            return transcription_pb2.TranscriptionResponse(
                transcript=transcript,
                success=True,
                error_message="",
                processing_time=processing_time,
                audio_duration=audio_duration,
                stats=transcription_pb2.TranscriptionStats(
                    word_count=word_count,
                    char_count=char_count,
                    speed_factor=speed_factor
                )
            )

        except Exception as e:
            error_msg = f"Ошибка при обработке стрима: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            processing_time = time.time() - start_time

            # Пытаемся удалить временный файл в случае ошибки
            try:
                if 'temp_audio_path' in locals():
                    Path(temp_audio_path).unlink()
            except:
                pass

            return transcription_pb2.TranscriptionResponse(
                transcript="",
                success=False,
                error_message=error_msg,
                processing_time=processing_time,
                audio_duration=0.0,
                stats=transcription_pb2.TranscriptionStats(
                    word_count=0,
                    char_count=0,
                    speed_factor=0.0
                )
            )

    def _get_transcription_pb2(self):
        """Возвращает модуль protobuf для версии v1"""
        return transcription_pb2

    def get_version(self) -> str:
        """Возвращает версию сервиса"""
        return "borealis"
