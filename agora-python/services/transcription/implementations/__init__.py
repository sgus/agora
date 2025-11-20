"""
Implementations Package

Содержит различные реализации сервиса транскрипции.

Доступные реализации:
    - BorealisTranscriptionService: Использует Borealis ML модель (Vikhrmodels/Borealis)
"""

from services.transcription.implementations.borealis_service import BorealisTranscriptionService

__all__ = [
    'BorealisTranscriptionService',
]
