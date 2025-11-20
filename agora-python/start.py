"""
Точка входа для запуска TranscriptionService gRPC сервера.

Использование:
    python start.py                                    # Запуск с параметрами по умолчанию
    python start.py --port 50052                       # Кастомный порт
    python start.py --implementation borealis          # Выбор реализации
    python start.py --port 50052 --implementation borealis
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from api.grpc.transcription_server import serve, AVAILABLE_IMPLEMENTATIONS


def main():
    """Главная функция запуска сервера"""
    parser = argparse.ArgumentParser(
        description='TranscriptionService gRPC Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python start.py
  python start.py --port 50052
  python start.py --implementation borealis
  python start.py --port 50052 --implementation borealis

Доступные реализации: {}
        """.format(', '.join(AVAILABLE_IMPLEMENTATIONS.keys()))
    )

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
        help='Реализация сервиса (по умолчанию: borealis)'
    )

    args = parser.parse_args()

    # Запуск сервера
    serve(port=args.port, implementation=args.implementation)


if __name__ == '__main__':
    main()
