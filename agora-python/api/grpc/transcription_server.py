"""
gRPC API Server для TranscriptionService.

Этот модуль отвечает за gRPC API слой - запускает сервер и маршрутизирует запросы
к соответствующим реализациям бизнес-логики.
"""

import sys
import grpc
from concurrent import futures
import time
import logging
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generated.v1 import transcription_pb2_grpc
from services.transcription.implementations.borealis_service import BorealisTranscriptionService
from resources.config import TranscriptionServiceConfig, config


# Доступные реализации сервиса
AVAILABLE_IMPLEMENTATIONS = {
    'borealis': BorealisTranscriptionService,
    # Здесь можно добавить другие реализации:
    # 'whisper': WhisperTranscriptionService,
    # 'google-speech': GoogleSpeechTranscriptionService,
    # 'azure': AzureTranscriptionService,
}


def serve(port=None, implementation='borealis'):
    """
    Запускает gRPC сервер TranscriptionService.

    Args:
        port: Порт для прослушивания (по умолчанию из config или 50051)
        implementation: Реализация сервиса ('borealis', 'whisper', 'google-speech', и т.д.)
    """
    # Используем порт из конфигурации если не указан
    if port is None:
        port = config.SERVER_PORT

    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT
    )
    logger = logging.getLogger(__name__)

    # Выбор реализации сервиса
    if implementation not in AVAILABLE_IMPLEMENTATIONS:
        logger.error(f"Неизвестная реализация сервиса: {implementation}")
        logger.info(f"Доступные реализации: {', '.join(AVAILABLE_IMPLEMENTATIONS.keys())}")
        return

    service_class = AVAILABLE_IMPLEMENTATIONS[implementation]
    service_impl = service_class()
    logger.info(f"Используется реализация: {implementation}")

    # Создание gRPC сервера с настройками из конфигурации
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', config.MAX_SEND_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', config.MAX_RECEIVE_MESSAGE_LENGTH),
        ]
    )
    transcription_pb2_grpc.add_TranscriptionServiceServicer_to_server(service_impl, server)

    # Привязка к порту
    server.add_insecure_port(f'[::]:{port}')

    # Запуск сервера
    server.start()

    logger.info("=" * 80)
    logger.info(f"🚀 TranscriptionService gRPC API ({implementation}) запущен на порту {port}")
    logger.info("=" * 80)
    logger.info(f"📡 Доступные методы:")
    logger.info(f"   - TranscribeAudio (унарный)")
    logger.info(f"   - TranscribeAudioStream (стриминговый)")
    logger.info("=" * 80)
    logger.info("💡 Нажмите Ctrl+C для остановки сервера")
    logger.info("=" * 80)

    try:
        # Держим сервер запущенным
        while True:
            time.sleep(86400)  # 24 часа
    except KeyboardInterrupt:
        logger.info("\n⏹️  Остановка сервера...")
        server.stop(0)
        logger.info("✅ Сервер остановлен")


if __name__ == '__main__':
    # Парсинг аргументов командной строки
    import argparse

    parser = argparse.ArgumentParser(description='TranscriptionService gRPC API Server')
    parser.add_argument(
        '--port',
        type=int,
        default=50051,
        help='Порт для прослушивания (по умолчанию: 50051)'
    )
    parser.add_argument(
        '--implementation',
        type=str,
        default='borealis',
        choices=list(AVAILABLE_IMPLEMENTATIONS.keys()),
        help=f'Реализация сервиса (по умолчанию: borealis)'
    )

    args = parser.parse_args()

    serve(port=args.port, implementation=args.implementation)
