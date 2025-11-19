"""
TranscriptionService версия 01.
Реализация gRPC сервиса для транскрипции аудио файлов с использованием ML модели.
"""

import sys
import time
import io
import tempfile
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generated.v1 import transcription_pb2
from generated.v1 import transcription_pb2_grpc
from services.base.transcription_service_base import TranscriptionServiceBase
from ml.transcribe import transcribe_interview
import librosa
import numpy as np


class TranscriptionService01(TranscriptionServiceBase, transcription_pb2_grpc.TranscriptionServiceServicer):
    """
    Реализация TranscriptionService версии 01.
    Принимает аудио файлы и возвращает заглушку с подтверждением получения.
    """

    def __init__(self):
        """Инициализация сервиса версии 01"""
        super().__init__()
        self.logger.info("TranscriptionService01 инициализирован")

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

        self.logger.info(f"Получен запрос на транскрипцию файла: {request.filename}")
        self.logger.info(f"Размер файла: {len(request.audio_data) / (1024*1024):.2f} МБ")
        self.logger.info(f"Формат: {request.format}")

        # Валидация запроса
        is_valid, error_msg = self._validate_transcription_request(request.filename, request.audio_data)

        if not is_valid:
            self.logger.error(f"Ошибка валидации: {error_msg}")
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

        # Транскрипция с использованием ML модели
        try:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=f".{request.format}", delete=False) as temp_file:
                temp_file.write(request.audio_data)
                temp_audio_path = temp_file.name

            self.logger.info(f"Временный файл создан: {temp_audio_path}")

            # Вычисляем длительность аудио
            try:
                waveform, sr = librosa.load(temp_audio_path, sr=16_000)
                audio_duration = len(waveform) / sr
                self.logger.info(f"Длительность аудио: {audio_duration:.1f} сек")
            except Exception as e:
                self.logger.warning(f"Не удалось вычислить длительность: {e}")
                audio_duration = 0.0

            # Запускаем транскрипцию
            self.logger.info("Запуск транскрипции...")
            transcript = transcribe_interview(temp_audio_path)

            # Удаляем временный файл
            try:
                Path(temp_audio_path).unlink()
            except Exception as e:
                self.logger.warning(f"Не удалось удалить временный файл: {e}")

            if transcript is None or transcript == "":
                raise Exception("Транскрипция вернула пустой результат")

            processing_time = time.time() - start_time
            word_count = len(transcript.split())
            char_count = len(transcript)
            speed_factor = audio_duration / processing_time if processing_time > 0 else 0.0

            self.logger.info(f"✅ Транскрипция успешно завершена!")
            self.logger.info(f"   Время обработки: {processing_time:.2f} сек")
            self.logger.info(f"   Скорость: {speed_factor:.1f}x от реального времени")
            self.logger.info(f"   Слов: {word_count}, Символов: {char_count}")

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
            self.logger.error(error_msg)
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

        self.logger.info("Получен стриминговый запрос на транскрипцию")

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
                    self.logger.info(f"Начало приема файла: {filename}")

                # Собираем данные
                chunks_data.append(chunk.chunk_data)

            # Объединяем все чанки
            audio_data = b''.join(chunks_data)
            actual_size = len(audio_data)

            self.logger.info(f"Получено {chunk_count} чанков, всего {actual_size / (1024*1024):.2f} МБ")

            # Валидация
            is_valid, error_msg = self._validate_transcription_request(filename, audio_data)

            if not is_valid:
                self.logger.error(f"Ошибка валидации: {error_msg}")
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

            # Транскрипция с использованием ML модели
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=f".{format_type}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_audio_path = temp_file.name

            self.logger.info(f"Временный файл создан: {temp_audio_path}")

            # Вычисляем длительность аудио
            try:
                waveform, sr = librosa.load(temp_audio_path, sr=16_000)
                audio_duration = len(waveform) / sr
                self.logger.info(f"Длительность аудио: {audio_duration:.1f} сек")
            except Exception as e:
                self.logger.warning(f"Не удалось вычислить длительность: {e}")
                audio_duration = 0.0

            # Запускаем транскрипцию
            self.logger.info("Запуск транскрипции...")
            transcript = transcribe_interview(temp_audio_path)

            # Удаляем временный файл
            try:
                Path(temp_audio_path).unlink()
            except Exception as e:
                self.logger.warning(f"Не удалось удалить временный файл: {e}")

            if transcript is None or transcript == "":
                raise Exception("Транскрипция вернула пустой результат")

            processing_time = time.time() - start_time
            word_count = len(transcript.split())
            char_count = len(transcript)
            speed_factor = audio_duration / processing_time if processing_time > 0 else 0.0

            self.logger.info(f"✅ Транскрипция успешно завершена!")
            self.logger.info(f"   Время обработки: {processing_time:.2f} сек")
            self.logger.info(f"   Скорость: {speed_factor:.1f}x от реального времени")
            self.logger.info(f"   Слов: {word_count}, Символов: {char_count}")

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
            self.logger.error(error_msg)
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
        """Возвращает модуль protobuf для версии 01"""
        return transcription_pb2

    def get_version(self) -> str:
        """Возвращает версию сервиса"""
        return "01"
