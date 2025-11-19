"""
Интерфейс для сервиса транскрипции.
Определяет контракт, который должны реализовывать все версии TranscriptionService.
"""

from abc import ABC, abstractmethod


class ITranscriptionService(ABC):
    """Интерфейс для сервиса транскрипции аудио файлов"""

    @abstractmethod
    def TranscribeAudio(self, request, context):
        """
        Транскрибирует аудио файл и возвращает текст.

        Args:
            request: AudioRequest с данными аудио файла
            context: gRPC context

        Returns:
            TranscriptionResponse с результатом транскрипции
        """
        pass

    @abstractmethod
    def TranscribeAudioStream(self, request_iterator, context):
        """
        Транскрибирует аудио файл через стрим и возвращает текст.

        Args:
            request_iterator: Итератор AudioChunk
            context: gRPC context

        Returns:
            TranscriptionResponse с результатом транскрипции
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Возвращает версию сервиса.

        Returns:
            Строка с версией (например, "01")
        """
        pass
