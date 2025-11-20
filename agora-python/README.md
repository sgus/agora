# Agora Python - gRPC Services

Этот проект содержит Python реализации gRPC сервисов для проекта Agora.

## Структура проекта

```
agora-python/
├── generated/              # Сгенерированные protobuf файлы
│   └── v1/
│       ├── audio_service_pb2.py
│       ├── audio_service_pb2_grpc.py
│       ├── transcription_pb2.py
│       └── transcription_pb2_grpc.py
├── services/               # Реализации сервисов
│   ├── base/              # Базовые классы и интерфейсы
│   │   ├── audio_service_interface.py
│   │   └── audio_service_base.py
│   ├── v1/                # Реализации версии 01
│   │   └── audio_service_01.py
│   └── audio_service.py   # Точка входа для AudioService
├── ml/                    # ML модели и скрипты
│   └── transcribe.py
├── uploads/               # Директория для загруженных файлов (создается автоматически)
├── generate_proto.bat     # Скрипт генерации protobuf
├── requirements.txt       # Зависимости проекта
└── test_audio_client.py   # Тестовый клиент

```

## Установка

### 1. Создать виртуальное окружение

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Установить зависимости

```powershell
pip install -r requirements.txt
```

## AudioService

Сервис для приема и обработки аудио файлов.

### Запуск сервера

```powershell
# Запуск с параметрами по умолчанию (порт 50052, версия 01)
python services/audio_service.py

# Запуск на другом порту
python services/audio_service.py --port 50053

# Запуск другой версии
python services/audio_service.py --version 01
```

### Тестирование

```powershell
# Тест с аудио файлом (оба метода: унарный и стриминговый)
python test_audio_client.py ml/audio.mp3

# Только унарный метод
python test_audio_client.py ml/audio.mp3 --method unary

# Только стриминговый метод
python test_audio_client.py ml/audio.mp3 --method stream

# Подключение к другому серверу
python test_audio_client.py ml/audio.mp3 --server localhost:50053

# Изменить размер чанка для стриминга
python test_audio_client.py ml/audio.mp3 --method stream --chunk-size 32768
```

### API методы

#### UploadAudio (унарный)
Принимает аудио файл целиком и возвращает подтверждение.

**Запрос:**
```protobuf
message AudioFileRequest {
  bytes audio_data = 1;
  string filename = 2;
  string format = 3;
  int64 file_size = 4;
}
```

**Ответ:**
```protobuf
message AudioFileResponse {
  string message = 1;              // "файл {name} получен"
  bool success = 2;
  string received_filename = 3;
  int64 received_size = 4;
  string error_message = 5;
}
```

#### UploadAudioStream (стриминговый)
Принимает аудио файл по частям (чанками) и возвращает подтверждение.

**Запрос (стрим):**
```protobuf
message AudioFileChunk {
  bytes chunk_data = 1;
  string filename = 2;      // Только в первом чанке
  string format = 3;        // Только в первом чанке
  int64 file_size = 4;      // Только в первом чанке
  int32 chunk_number = 5;
}
```

**Ответ:**
```protobuf
message AudioFileResponse {
  // Такой же как в UploadAudio
}
```

## Генерация protobuf файлов

После изменения `.proto` файлов в директории `proto/`, запустите:

```powershell
.\generate_proto.bat
```

Это сгенерирует Python классы в директории `generated/v1/`.

## Архитектура версионирования

Проект следует паттерну версионирования, описанному в `proto/VERSIONING.md`:

1. **Интерфейс** (`IAudioService`) - определяет контракт
2. **Базовый класс** (`AudioServiceBase`) - общая логика
3. **Реализация** (`AudioService01`) - специфичная логика для версии 01

### Добавление новой версии

1. Создать `proto/v2/audio_service.proto`
2. Обновить `generate_proto.bat`
3. Создать `services/v2/audio_service_02.py`
4. Обновить `services/audio_service.py` для поддержки версии 02

## Поддерживаемые форматы аудио

- `.mp3`
- `.wav`
- `.m4a`
- `.flac`
- `.ogg`
- `.aac`

## Логирование

Все сервисы используют стандартное Python логирование. Логи выводятся в консоль с форматом:

```
YYYY-MM-DD HH:MM:SS - ServiceName - LEVEL - Message
```

## Хранилище файлов

Загруженные файлы сохраняются в директории `uploads/` с уникальными именами:

```
uploads/YYYYMMDD_HHMMSS_original_filename.ext
```

## Troubleshooting

### ModuleNotFoundError: No module named 'grpc_tools'

```powershell
pip install grpcio-tools
```

### Ошибка подключения к серверу

Убедитесь, что сервер запущен:
```powershell
python services/audio_service.py
```

### Файл не найден при тестировании

Проверьте путь к аудио файлу:
```powershell
python test_audio_client.py path/to/your/audio.mp3
```
