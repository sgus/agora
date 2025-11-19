# Настройка версионности - Инструкция

Этот документ содержит пошаговую инструкцию по настройке версионированной архитектуры для проекта Agora.

## Что было создано

### 1. Proto файлы
- ✅ `proto/v1/transcription.proto` - Версионированный proto файл для API v1
- ✅ `proto/VERSIONING.md` - Полная документация по версионности
- ✅ Обновлен `proto/README.md`

### 2. Python сервисы
- ✅ `agora-python/services/base/transcription_service_interface.py` - Интерфейс
- ✅ `agora-python/services/base/transcription_service_base.py` - Абстрактный класс
- ✅ `agora-python/services/v1/transcription_service_01.py` - Реализация v01
- ✅ Обновлен `agora-python/services/transcription_service.py` - Точка входа

### 3. Java клиенты
- ✅ `agora-backend/src/main/java/ai/agorabackend/service/base/ITranscriptionClient.java` - Интерфейс
- ✅ `agora-backend/src/main/java/ai/agorabackend/service/base/TranscriptionClientBase.java` - Абстрактный класс
- ✅ `agora-backend/src/main/java/ai/agorabackend/service/v1/TranscriptionClientService01.java` - Реализация v01
- ✅ Обновлен `agora-backend/src/main/java/ai/agorabackend/service/TranscriptionClientService.java` - Фасад

## Шаги для завершения настройки

### Шаг 1: Генерация proto классов для Java

```bash
# Из корневой директории проекта
./gradlew :agora-backend:generateProto
```

Это создаст классы в пакете `ai.agora.proto.v1`:
- `AudioRequest`
- `TranscriptionResponse`
- `TranscriptionServiceGrpc`
- И другие

### Шаг 2: Раскомментировать код в TranscriptionClientService01

После генерации proto классов, откройте файл:
`agora-backend/src/main/java/ai/agorabackend/service/v1/TranscriptionClientService01.java`

И раскомментируйте:

1. **Импорты** (в начале файла):
```java
import ai.agora.proto.v1.AudioRequest;
import ai.agora.proto.v1.TranscriptionResponse;
import ai.agora.proto.v1.TranscriptionServiceGrpc;
```

2. **Поле blockingStub**:
```java
private TranscriptionServiceGrpc.TranscriptionServiceBlockingStub blockingStub;
```

3. **Метод initStub()**:
```java
@Override
protected void initStub() {
    blockingStub = TranscriptionServiceGrpc.newBlockingStub(channel);
    logger.info("✓ Blocking stub инициализирован для версии 01");
}
```

4. **Метод transcribeAudio()** - удалите временный код и раскомментируйте полную реализацию

### Шаг 3: Генерация proto классов для Python

```bash
cd agora-python
generate_proto.bat
```

Или вручную:
```bash
cd agora-python
python -m grpc_tools.protoc -I../proto/v1 --python_out=./generated --grpc_python_out=./generated ../proto/v1/transcription.proto
```

### Шаг 4: Обновить импорты в Python (если нужно)

Убедитесь, что в `agora-python/services/v1/transcription_service_01.py` правильные импорты для сгенерированных классов.

### Шаг 5: Настроить application.properties

В `agora-backend/src/main/resources/application.properties` добавьте:

```properties
# Версия клиента транскрипции (01, 02, и т.д.)
transcription.client.version=01

# gRPC настройки (если еще не добавлены)
transcription.grpc.host=localhost
transcription.grpc.port=50051
```

### Шаг 6: Тестирование

#### Запуск Python сервера:
```bash
cd agora-python
python services/transcription_service.py 01
```

#### Запуск Java приложения:
```bash
./gradlew :agora-backend:bootRun
```

## Проверка работы

### 1. Проверка Python сервера
При запуске вы должны увидеть:
```
Инициализация TranscriptionService01...
Инициализация TranscriptionEngine для версии 01...
✓ TranscriptionEngine инициализирован
TranscriptionService01 готов к работе
Запуск gRPC сервера на порту 50051...
✓ gRPC сервер запущен на порту 50051 (версия 01)
```

### 2. Проверка Java клиента
При запуске вы должны увидеть:
```
Инициализация TranscriptionClientService01...
Подключение к gRPC серверу: localhost:50051
✓ Blocking stub инициализирован для версии 01
✓ TranscriptionClientService01 инициализирован (версия 01)
```

## Добавление новой версии (v02)

Когда потребуется создать версию 02:

### 1. Создать proto файл
```bash
# Создать proto/v2/transcription.proto
# Скопировать из v1 и внести изменения
```

### 2. Создать Python реализацию
```bash
# Создать agora-python/services/v2/transcription_service_02.py
```

### 3. Создать Java клиент
```bash
# Создать agora-backend/src/main/java/ai/agorabackend/service/v2/TranscriptionClientService02.java
```

### 4. Обновить фасады
- В `transcription_service.py` добавить обработку версии '02'
- В `TranscriptionClientService.java` добавить case для версии "02"

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        Proto Files                          │
│  proto/v1/transcription.proto → proto/v2/transcription.proto│
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        ↓                                           ↓
┌───────────────────┐                    ┌──────────────────────┐
│  Python Services  │                    │    Java Clients      │
├───────────────────┤                    ├──────────────────────┤
│  ITranscription   │                    │  ITranscription      │
│    Service        │                    │    Client            │
│  (interface)      │                    │  (interface)         │
│        ↓          │                    │        ↓             │
│  Transcription    │                    │  Transcription       │
│   ServiceBase     │                    │   ClientBase         │
│  (abstract)       │                    │  (abstract)          │
│        ↓          │                    │        ↓             │
│  ┌──────────────┐ │                    │  ┌─────────────────┐ │
│  │ Service01    │ │                    │  │ ClientService01 │ │
│  │ Service02    │ │                    │  │ ClientService02 │ │
│  └──────────────┘ │                    │  └─────────────────┘ │
└───────────────────┘                    └──────────────────────┘
```

## Полезные команды

```bash
# Сборка всего проекта
./gradlew build

# Генерация только proto для Java
./gradlew :agora-backend:generateProto

# Запуск Python сервера с версией
python agora-python/services/transcription_service.py 01

# Запуск Java приложения
./gradlew :agora-backend:bootRun

# Проверка логов
tail -f agora-backend/logs/application.log
```

## Troubleshooting

### Ошибка: Cannot resolve symbol 'agora'
- Запустите генерацию proto: `./gradlew :agora-backend:generateProto`
- Обновите проект в IDE (Reload Gradle Project)

### Ошибка: Module not found в Python
- Проверьте, что proto классы сгенерированы в `agora-python/generated/`
- Убедитесь, что путь к generated добавлен в sys.path

### Сервер не запускается
- Проверьте, что порт 50051 свободен
- Убедитесь, что все зависимости установлены

## Дополнительная информация

Полная документация по версионности: [proto/VERSIONING.md](proto/VERSIONING.md)
