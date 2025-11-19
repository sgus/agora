"""
Конфигурация для TranscriptionService.
Все настройки сервиса в одном месте.
"""

import os
from pathlib import Path


class TranscriptionServiceConfig:
    """Конфигурация для TranscriptionService"""

    # ========================================
    # Настройки сервера
    # ========================================

    # Порт для прослушивания gRPC сервера
    SERVER_PORT = int(os.getenv('TRANSCRIPTION_SERVICE_PORT', '50051'))

    # Версия сервиса по умолчанию
    SERVICE_VERSION = os.getenv('TRANSCRIPTION_SERVICE_VERSION', '01')

    # Максимальное количество worker потоков
    MAX_WORKERS = int(os.getenv('TRANSCRIPTION_SERVICE_MAX_WORKERS', '10'))

    # Адрес для прослушивания (по умолчанию все интерфейсы)
    SERVER_HOST = os.getenv('TRANSCRIPTION_SERVICE_HOST', '[::]')

    # ========================================
    # Настройки ML модели
    # ========================================

    # Путь к модели транскрипции
    MODEL_NAME = os.getenv('TRANSCRIPTION_MODEL_NAME', 'Vikhrmodels/Borealis')

    # Использовать локальные файлы модели
    MODEL_LOCAL_FILES_ONLY = os.getenv('TRANSCRIPTION_MODEL_LOCAL', 'true').lower() == 'true'

    # Устройство для обработки (cuda, cpu)
    DEVICE = os.getenv('TRANSCRIPTION_DEVICE', 'cuda')

    # Batch size для обработки
    BATCH_SIZE = int(os.getenv('TRANSCRIPTION_BATCH_SIZE', '32'))

    # Целевая длительность чанка в секундах
    TARGET_CHUNK_DURATION = int(os.getenv('TRANSCRIPTION_CHUNK_DURATION', '30'))

    # ========================================
    # Настройки производительности
    # ========================================

    # Максимальный размер сообщения для отправки (в байтах)
    MAX_SEND_MESSAGE_LENGTH = int(os.getenv('TRANSCRIPTION_MAX_SEND_MSG', str(200 * 1024 * 1024)))

    # Максимальный размер сообщения для получения (в байтах)
    MAX_RECEIVE_MESSAGE_LENGTH = int(os.getenv('TRANSCRIPTION_MAX_RECV_MSG', str(200 * 1024 * 1024)))


# Создаем глобальный экземпляр конфигурации
config = TranscriptionServiceConfig()
