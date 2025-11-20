"""
Services Package

Содержит все gRPC сервисы приложения.

Доступные сервисы:
    - transcription: Сервис транскрипции аудио файлов
"""

from services.transcription import (
    ITranscriptionService,
    TranscriptionServiceBase,
    BorealisTranscriptionService,
)

__all__ = [
    'ITranscriptionService',
    'TranscriptionServiceBase',
    'BorealisTranscriptionService',
]
