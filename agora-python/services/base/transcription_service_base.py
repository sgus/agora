"""
Базовый абстрактный класс для сервиса транскрипции аудио файлов.
Содержит общую логику для всех версий.
"""

import logging
import time
from abc import abstractmethod
from pathlib import Path

from services.base.transcription_service_interface import ITranscriptionService


class TranscriptionServiceBase(ITranscriptionService):
    """Базовый класс с общей логикой для всех версий TranscriptionService"""

    def __init__(self):
        """Инициализация базового сервиса"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _validate_transcription_request(self, filename: str, audio_data: bytes) -> tuple[bool, str]:
        """
        Валидация запроса на транскрипцию.

        Args:
            filename: Имя файла
            audio_data: Данные файла

        Returns:
            Tuple (is_valid, error_message)
        """
        if not filename:
            return False, "Имя файла не указано"

        if not audio_data or len(audio_data) == 0:
            return False, "Данные файла пустые"

        # Проверка расширения файла
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
        file_ext = Path(filename).suffix.lower()

        if file_ext not in allowed_extensions:
            return False, f"Неподдерживаемый формат файла: {file_ext}"

        return True, ""

    def _calculate_audio_duration(self, audio_data: bytes) -> float:
        """
        Вычисляет длительность аудио (заглушка).

        Args:
            audio_data: Данные аудио файла

        Returns:
            Длительность в секундах (пока возвращаем 0.0)
        """
        # TODO: Реализовать реальное вычисление длительности
        return 0.0

    @abstractmethod
    def _get_transcription_pb2(self):
        """
        Возвращает модуль protobuf для конкретной версии.
        Должен быть реализован в подклассе.

        Returns:
            Модуль transcription_pb2 для конкретной версии
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Возвращает версию сервиса.
        Должен быть реализован в подклассе.

        Returns:
            Строка с версией (например, "01")
        """
        pass
