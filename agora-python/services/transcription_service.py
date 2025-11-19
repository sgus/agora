"""
Точка входа для TranscriptionService.
Запускает gRPC сервер с выбранной версией сервиса.
"""

import sys
import grpc
from concurrent import futures
import time
import logging
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from generated.v1 import transcription_pb2_grpc
from services.v1.transcription_service_01 import TranscriptionService01
from config import TranscriptionServiceConfig


def serve(port=None, version=None):
    """
    Запускает gRPC сервер TranscriptionService.

    Args:
        port: Порт для прослушивания (по умолчанию 50051)
        version: Версия сервиса ('01', '02', и т.д.)
    """
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Выбор версии сервиса
    if version == '01':
        service_impl = TranscriptionService01()
        logger.info("Используется TranscriptionService версии 01")
    else:
        logger.error(f"Неизвестная версия сервиса: {version}")
        logger.info("Доступные версии: 01")
        return

    # Создание gRPC сервера с увеличенным лимитом размера сообщений
    # Устанавливаем лимит в 200 МБ для приема и отправки сообщений
    max_message_length = 200 * 1024 * 1024  # 200 MB

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', max_message_length),
            ('grpc.max_receive_message_length', max_message_length),
        ]
    )
    transcription_pb2_grpc.add_TranscriptionServiceServicer_to_server(service_impl, server)

    # Привязка к порту
    server.add_insecure_port(f'[::]:{port}')

    # Запуск сервера
    server.start()

    logger.info("=" * 80)
    logger.info(f"TranscriptionService v{version} запущен на порту {port}")
    logger.info("=" * 80)
    logger.info(f"Доступные методы:")
    logger.info(f"  - TranscribeAudio (унарный)")
    logger.info(f"  - TranscribeAudioStream (стриминговый)")
    logger.info("=" * 80)
    logger.info("Нажмите Ctrl+C для остановки сервера")
    logger.info("=" * 80)

    try:
        # Держим сервер запущенным
        while True:
            time.sleep(86400)  # 24 часа
    except KeyboardInterrupt:
        logger.info("\nОстановка сервера...")
        server.stop(0)
        logger.info("Сервер остановлен")


if __name__ == '__main__':
    # Парсинг аргументов командной строки
    import argparse

    parser = argparse.ArgumentParser(description='TranscriptionService gRPC Server')
    parser.add_argument(
        '--port',
        type=int,
        default=50051,
        help='Порт для прослушивания (по умолчанию: 50051)'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='01',
        help='Версия сервиса (по умолчанию: 01)'
    )

    args = parser.parse_args()

    serve(port=args.port, version=args.version)
