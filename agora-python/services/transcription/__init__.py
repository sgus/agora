"""
Transcription Service Package

Этот пакет содержит бизнес-логику для сервиса транскрипции аудио файлов.

Структура:
    - interface.py: Интерфейс ITranscriptionService
    - base_service.py: Базовый класс с общей логикой
    - implementations/: Конкретные реализации сервиса
        - borealis_service.py: Реализация с использованием Borealis модели

Использование:
    from services.transcription import BorealisTranscriptionService

Документация: См. главный README.md в корне проекта
"""

from services.transcription.interface import ITranscriptionService
from services.transcription.base_service import TranscriptionServiceBase
from services.transcription.implementations.borealis_service import BorealisTranscriptionService

__all__ = [
    'ITranscriptionService',
    'TranscriptionServiceBase',
    'BorealisTranscriptionService',
]
