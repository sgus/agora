# Agora Python - TranscriptionService

Проект содержит gRPC сервис транскрипции аудио файлов с использованием ML модели Borealis (Vikhrmodels/Borealis).

## 🏗️ Архитектура проекта

Проект следует принципу **разделения API и бизнес-логики**:

```
agora-python/
├── api/                            # API слой (gRPC серверы)
│   └── grpc/
│       └── transcription_server.py # gRPC сервер для транскрипции
│
├── services/                       # Бизнес-логика
│   └── transcription/
│       ├── interface.py           # Интерфейс ITranscriptionService
│       ├── base_service.py        # Базовый класс с общей логикой
│       └── implementations/       # Конкретные реализации
│           └── borealis_service.py # Реализация с Borealis ML моделью
│
├── resources/                      # Конфигурация и ресурсы
│   ├── .env.example              # Пример конфигурации (скопируйте в .env)
│   └── config.py                 # Загрузчик конфигурации
│
├── generated/                      # Сгенерированные protobuf файлы
│   └── v1/
│       ├── transcription_pb2.py
│       └── transcription_pb2_grpc.py
│
├── ml/                            # ML модели и скрипты
├── start.py                       # 🚀 Точка входа для запуска сервера
├── requirements.txt               # Зависимости
└── generate_proto.bat             # Генерация protobuf файлов
```

### Разделение ответственности

**`api/grpc/`** - API слой:
- ✅ Запуск gRPC серверов
- ✅ Маршрутизация запросов
- ✅ Конфигурация gRPC (размер сообщений, воркеры)

**`services/`** - Бизнес-логика:
- ✅ Интерфейсы и контракты
- ✅ Реализации сервисов
- ✅ Обработка данных и ML модели

## 🚀 Быстрый старт

### 1. Установка

```powershell
# Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt

# Установить PyTorch с CUDA 13.0 (для GPU)
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130

# Или для CPU only
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cpu
```

### 2. Генерация protobuf файлов

```powershell
.\generate_proto.bat
```

### 3. Конфигурация

Скопируйте пример конфигурации и настройте под свои нужды:

```powershell
# Создайте .env файл из примера
Copy-Item resources\.env.example .env

# Отредактируйте .env файл под свои нужды
# Все настройки можно также задать через переменные окружения
```

**Доступные настройки:**
- `MODEL_NAME` - название ML модели (по умолчанию: `Vikhrmodels/Borealis`)
- `MODEL_DEVICE` - устройство для обработки: `cuda` или `cpu` (по умолчанию: `cuda`)
- `MODEL_BATCH_SIZE` - размер батча для обработки (по умолчанию: `32`)
- `MODEL_CHUNK_DURATION` - длительность чанка в секундах (по умолчанию: `30`)
- `SERVER_PORT` - порт gRPC сервера (по умолчанию: `50051`)
- `LOGGING_LEVEL` - уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR` (по умолчанию: `INFO`)

Полный список настроек смотрите в `resources/.env.example`

### 4. Запуск gRPC сервера

```powershell
# 🚀 Простой запуск (рекомендуется)
python start.py

# С кастомными параметрами
python start.py --port 50052
python start.py --implementation borealis
python start.py --port 50052 --implementation borealis

# Альтернативный способ (прямой запуск)
python api/grpc/transcription_server.py --port 50051
```

## 📡 TranscriptionService API

### Методы

#### 1. TranscribeAudio (унарный)
Принимает аудио файл целиком и возвращает транскрипцию.

**Запрос:**
```protobuf
message AudioRequest {
  bytes audio_data = 1;
  string filename = 2;
  string format = 3;
}
```

**Ответ:**
```protobuf
message TranscriptionResponse {
  string transcript = 1;
  bool success = 2;
  string error_message = 3;
  double processing_time = 4;
  double audio_duration = 5;
  TranscriptionStats stats = 6;
}

message TranscriptionStats {
  int32 word_count = 1;
  int32 char_count = 2;
  double speed_factor = 3;
}
```

#### 2. TranscribeAudioStream (стриминговый)
Принимает аудио файл по частям (чанками) и возвращает транскрипцию.

**Запрос (стрим):**
```protobuf
message AudioChunk {
  bytes chunk_data = 1;
  string filename = 2;      // Только в первом чанке
  string format = 3;        // Только в первом чанке
  int32 sample_rate = 4;    // Только в первом чанке
}
```

**Ответ:** Такой же как в `TranscribeAudio`

### Поддерживаемые форматы

✅ MP3, WAV, M4A, FLAC, OGG, AAC

## 🤖 Borealis ML модель

### Особенности реализации

**Production v4.0 (FULLY OPTIMIZED)**:
- ✅ **Batch Size 32** - оптимальный для RTX 5080
- ✅ **Pinned Memory** - быстрое DMA копирование CPU→GPU
- ✅ **Асинхронная обработка** - GPU и CPU работают параллельно
- ✅ **CUDA Streams** - non-blocking transfer
- ✅ **Умное разрезание** - по паузам с сохранением контекста

### Производительность

- **Скорость**: ~10-15x от реального времени (на RTX 5080)
- **Точность**: Высокая точность транскрипции русского языка
- **Память GPU**: ~8-12 GB в зависимости от длины аудио

## ⚙️ Конфигурация

### Способы конфигурации (по приоритету):

1. **Переменные окружения** (высший приоритет)
2. **`.env` файл** в корне проекта
3. **Значения по умолчанию** в коде

Это стандартный подход для Python проектов (как в Django, Flask, FastAPI).

### Создание .env файла

```powershell
# Скопируйте пример конфигурации
Copy-Item resources\.env.example .env

# Отредактируйте .env под свои нужды
notepad .env
```

### Пример .env файла:

```bash
# Настройки сервера
SERVER_PORT=50051
SERVER_HOST=[::]
SERVER_MAX_WORKERS=10

# ML модель
MODEL_NAME=Vikhrmodels/Borealis
MODEL_DEVICE=cuda
MODEL_BATCH_SIZE=32
MODEL_CHUNK_DURATION=30

# Производительность
GRPC_MAX_SEND_MESSAGE_LENGTH=209715200
GRPC_MAX_RECEIVE_MESSAGE_LENGTH=209715200

# Логирование
LOGGING_LEVEL=INFO
```

### Переопределение через переменные окружения:

```powershell
# PowerShell
$env:SERVER_PORT = "50052"
$env:MODEL_DEVICE = "cpu"
$env:MODEL_BATCH_SIZE = "16"

# Затем запустите
python start.py
```

```bash
# Linux/Mac
export SERVER_PORT=50052
export MODEL_DEVICE=cpu
export MODEL_BATCH_SIZE=16

python start.py
```

## 🔧 Разработка

### Добавление новой реализации

Например, добавим Google Speech:

1. **Создайте реализацию** `services/transcription/implementations/google_speech_service.py`:

```python
from services.transcription.base_service import TranscriptionServiceBase
from generated.v1 import transcription_pb2_grpc

class GoogleSpeechTranscriptionService(TranscriptionServiceBase,
                                       transcription_pb2_grpc.TranscriptionServiceServicer):
    def __init__(self):
        super().__init__()
        # Инициализация Google Speech API

    def TranscribeAudio(self, request, context):
        # Реализация
        pass

    def TranscribeAudioStream(self, request_iterator, context):
        # Реализация
        pass

    def get_version(self) -> str:
        return "google-speech"
```

2. **Обновите** `services/transcription/implementations/__init__.py`:

```python
from services.transcription.implementations.borealis_service import BorealisTranscriptionService
from services.transcription.implementations.google_speech_service import GoogleSpeechTranscriptionService

__all__ = [
    'BorealisTranscriptionService',
    'GoogleSpeechTranscriptionService',
]
```

3. **Добавьте в** `api/grpc/transcription_server.py`:

```python
AVAILABLE_IMPLEMENTATIONS = {
    'borealis': BorealisTranscriptionService,
    'google-speech': GoogleSpeechTranscriptionService,
}
```

4. **Запустите**:

```powershell
python api/grpc/transcription_server.py --implementation google-speech
```

### Генерация protobuf после изменений

После изменения `.proto` файлов в `../proto/`:

```powershell
.\generate_proto.bat
```

## 📊 Логирование

Все сервисы используют стандартное Python логирование с детальным выводом:

```
2024-01-15 10:30:45 - BorealisTranscriptionService - INFO - ================================================================================
2024-01-15 10:30:45 - BorealisTranscriptionService - INFO - 📥 Получен запрос на транскрипцию файла: interview.mp3
2024-01-15 10:30:45 - BorealisTranscriptionService - INFO -    Размер файла: 15.23 МБ
2024-01-15 10:30:45 - BorealisTranscriptionService - INFO -    Формат: mp3
2024-01-15 10:30:45 - BorealisTranscriptionService - INFO - ================================================================================
2024-01-15 10:30:50 - BorealisTranscriptionService - INFO - ✅ Транскрипция успешно завершена!
2024-01-15 10:30:50 - BorealisTranscriptionService - INFO -    Общее время обработки: 5.23 сек
2024-01-15 10:30:50 - BorealisTranscriptionService - INFO -    Скорость: 12.5x от реального времени
2024-01-15 10:30:50 - BorealisTranscriptionService - INFO -    Слов: 1234, Символов: 5678
```

## 🧪 Тестирование

### Создание тестового клиента

```python
import grpc
from generated.v1 import transcription_pb2, transcription_pb2_grpc

# Подключение к серверу
channel = grpc.insecure_channel('localhost:50051')
stub = transcription_pb2_grpc.TranscriptionServiceStub(channel)

# Чтение аудио файла
with open('audio.mp3', 'rb') as f:
    audio_data = f.read()

# Отправка запроса
request = transcription_pb2.AudioRequest(
    audio_data=audio_data,
    filename='audio.mp3',
    format='mp3'
)

response = stub.TranscribeAudio(request)

print(f"Транскрипция: {response.transcript}")
print(f"Время обработки: {response.processing_time:.2f}s")
print(f"Скорость: {response.stats.speed_factor:.1f}x")
```

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'grpc_tools'

```powershell
pip install grpcio-tools
```

### CUDA out of memory

Уменьшите batch size в `config.py`:
```python
BATCH_SIZE = 16  # вместо 32
```

### Модель не найдена

Убедитесь, что модель Borealis загружена локально:
```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("Vikhrmodels/Borealis", trust_remote_code=True)
```

### Ошибка подключения к серверу

Проверьте, что сервер запущен:
```powershell
python api/grpc/transcription_server.py
```

## 📚 Дополнительная документация

- **API слой**: `api/grpc/README.md`
- **Бизнес-логика**: `services/transcription/README.md`
- **Protobuf**: `../proto/VERSIONING.md`

## 📄 Лицензия

[Укажите лицензию проекта]

## 👥 Авторы

[Укажите авторов проекта]
