"""
Resources Package

Содержит конфигурационные файлы и ресурсы приложения.

Файлы:
    - application.properties: Основная конфигурация (стиль Spring Boot)
    - .env.example: Пример файла переменных окружения
    - config.py: Загрузчик конфигурации
"""

from resources.config import config, TranscriptionServiceConfig

__all__ = ['config', 'TranscriptionServiceConfig']
