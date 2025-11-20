"""
Конфигурация для TranscriptionService.

Загружает настройки из:
1. Переменные окружения (высший приоритет)
2. .env файл в корне проекта (если существует)
3. Значения по умолчанию

Это стандартный подход для Python проектов.
Для использования .env файла установите: pip install python-dotenv
"""

import os
from pathlib import Path


def load_env_file():
    """
    Загружает .env файл если он существует.
    Использует простой парсер без зависимостей.
    """
    env_file = Path(__file__).parent.parent / '.env'

    if not env_file.exists():
        return

    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Пропускаем комментарии и пустые строки
            if not line or line.startswith('#'):
                continue

            # Парсим KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Устанавливаем только если еще не установлено
                if key not in os.environ:
                    os.environ[key] = value


# Загружаем .env файл при импорте модуля
load_env_file()


def get_env(key: str, default=None, cast_type=str):
    """
    Получить значение из переменных окружения с приведением типа.

    Args:
        key: Ключ переменной окружения
        default: Значение по умолчанию
        cast_type: Тип для приведения (str, int, bool, float)

    Returns:
        Значение с приведенным типом
    """
    value = os.getenv(key)

    if value is None:
        return default

    # Приведение типа
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    elif cast_type == float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    else:
        return value


class TranscriptionServiceConfig:
    """
    Конфигурация для TranscriptionService.

    Все настройки загружаются из переменных окружения или .env файла.
    """

    # ========================================
    # Настройки сервера
    # ========================================

    @property
    def SERVER_PORT(self) -> int:
        """Порт для прослушивания gRPC сервера"""
        return get_env('SERVER_PORT', 50051, int)

    @property
    def SERVER_HOST(self) -> str:
        """Адрес для прослушивания"""
        return get_env('SERVER_HOST', '[::]')

    @property
    def MAX_WORKERS(self) -> int:
        """Максимальное количество worker потоков"""
        return get_env('SERVER_MAX_WORKERS', 10, int)

    # ========================================
    # Настройки ML модели
    # ========================================

    @property
    def MODEL_NAME(self) -> str:
        """Название модели"""
        return get_env('MODEL_NAME', 'Vikhrmodels/Borealis')

    @property
    def MODEL_LOCAL_FILES_ONLY(self) -> bool:
        """Использовать локальные файлы модели"""
        return get_env('MODEL_LOCAL_FILES_ONLY', True, bool)

    @property
    def DEVICE(self) -> str:
        """Устройство для обработки (cuda, cpu)"""
        return get_env('MODEL_DEVICE', 'cuda')

    @property
    def BATCH_SIZE(self) -> int:
        """Batch size для обработки"""
        return get_env('MODEL_BATCH_SIZE', 32, int)

    @property
    def TARGET_CHUNK_DURATION(self) -> int:
        """Целевая длительность чанка в секундах"""
        return get_env('MODEL_CHUNK_DURATION', 30, int)

    # ========================================
    # Настройки производительности
    # ========================================

    @property
    def MAX_SEND_MESSAGE_LENGTH(self) -> int:
        """Максимальный размер сообщения для отправки (в байтах)"""
        return get_env('GRPC_MAX_SEND_MESSAGE_LENGTH', 200 * 1024 * 1024, int)

    @property
    def MAX_RECEIVE_MESSAGE_LENGTH(self) -> int:
        """Максимальный размер сообщения для получения (в байтах)"""
        return get_env('GRPC_MAX_RECEIVE_MESSAGE_LENGTH', 200 * 1024 * 1024, int)

    # ========================================
    # Настройки логирования
    # ========================================

    @property
    def LOG_LEVEL(self) -> str:
        """Уровень логирования"""
        return get_env('LOGGING_LEVEL', 'INFO')

    @property
    def LOG_FORMAT(self) -> str:
        """Формат логов"""
        return get_env('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# Создаем глобальный экземпляр конфигурации
config = TranscriptionServiceConfig()
