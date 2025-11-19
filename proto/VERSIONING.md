# Версионность Proto файлов и сервисов

## Обзор

Проект использует версионированную архитектуру для proto файлов и сервисов, что позволяет:
- Поддерживать несколько версий API одновременно
- Безопасно вносить breaking changes в новых версиях
- Обеспечивать обратную совместимость для существующих клиентов

## Структура версионирования

### Proto файлы

Proto файлы организованы по версиям в директории `proto/`:

```
proto/
├── v1/
│   └── transcription.proto  # Версия 1 API
├── v2/                       # Будущая версия 2
│   └── transcription.proto
└── transcription.proto       # Legacy (deprecated)
```

**Важно:**
- Каждая версия имеет свой package: `transcription.v1`, `transcription.v2`, и т.д.
- Java package также версионирован: `ai.agora.proto.v1`, `ai.agora.proto.v2`
- Legacy файл `transcription.proto` сохранен для обратной совместимости

### Python сервисы

Сервисы организованы с использованием паттерна "Интерфейс → Абстрактный класс → Реализация":

```
agora-python/services/
├── base/
│   ├── __init__.py
│   ├── transcription_service_interface.py  # ITranscriptionService (интерфейс)
│   └── transcription_service_base.py       # TranscriptionServiceBase (абстрактный класс)
├── v1/
│   ├── __init__.py
│   └── transcription_service_01.py         # TranscriptionService01 (реализация v1)
├── v2/                                      # Будущая версия 2
│   ├── __init__.py
│   └── transcription_service_02.py         # TranscriptionService02 (реализация v2)
└── transcription_service.py                # Точка входа (запуск сервера)
```

#### Архитектура Python сервисов

1. **ITranscriptionService** (интерфейс)
   - Определяет контракт для всех версий сервиса
   - Методы: `TranscribeAudio()`, `TranscribeAudioStream()`

2. **TranscriptionServiceBase** (абстрактный класс)
   - Наследует `ITranscriptionService`
   - Содержит общую логику: работа с файлами, обработка ошибок, логирование
   - Абстрактные методы: `_init_engine()`, `_get_transcription_pb2()`, `_transcribe_file()`

3. **TranscriptionService01** (конкретная реализация)
   - Наследует `TranscriptionServiceBase`
   - Имплементирует `TranscriptionServiceServicer` из protobuf
   - Реализует специфичную логику для версии 01

### Java клиенты

Клиенты также следуют паттерну версионирования:

```
agora-backend/src/main/java/ai/agorabackend/service/
├── base/
│   ├── ITranscriptionClient.java           # Интерфейс клиента
│   └── TranscriptionClientBase.java        # Абстрактный базовый класс
├── v1/
│   └── TranscriptionClientService01.java   # Реализация клиента v1
├── v2/                                      # Будущая версия 2
│   └── TranscriptionClientService02.java
└── TranscriptionClientService.java         # Фасад (делегирует к версиям)
```

#### Архитектура Java клиентов

1. **ITranscriptionClient** (интерфейс)
   - Определяет контракт для всех версий клиента
   - Методы: `transcribeAudio()`, `getVersion()`, `init()`, `shutdown()`

2. **TranscriptionClientBase** (абстрактный класс)
   - Имплементирует `ITranscriptionClient`
   - Содержит общую логику: подключение к gRPC, работа с файлами, логирование
   - Абстрактный метод: `initStub()`

3. **TranscriptionClientService01** (конкретная реализация)
   - Наследует `TranscriptionClientBase`
   - Использует `ai.agora.proto.v1` для работы с версией 01 API
   - Аннотирован `@Service` для Spring

4. **TranscriptionClientService** (фасад)
   - Делегирует вызовы к конкретной версии клиента
   - Версия настраивается через `application.properties`

## Использование

### Запуск Python сервера с определенной версией

```bash
# Версия 01 (по умолчанию)
python agora-python/services/transcription_service.py

# Явное указание версии
python agora-python/services/transcription_service.py 01

# Будущая версия 02
python agora-python/services/transcription_service.py 02
```

### Настройка версии в Java клиенте

В `application.properties`:

```properties
# Версия клиента транскрипции (01, 02, и т.д.)
transcription.client.version=01
```

### Создание новой версии

#### 1. Создать новый proto файл

```bash
# Создать proto/v2/transcription.proto
```

Обновить package и java_package:
```protobuf
syntax = "proto3";

option java_multiple_files = true;
option java_package = "ai.agora.proto.v2";
option java_outer_classname = "TranscriptionProtoV2";

package transcription.v2;
```

#### 2. Создать Python реализацию

```bash
# Создать agora-python/services/v2/transcription_service_02.py
```

```python
from services.base import TranscriptionServiceBase

class TranscriptionService02(TranscriptionServiceBase, transcription_pb2_grpc.TranscriptionServiceServicer):
    def __init__(self):
        super().__init__()

    def _init_engine(self):
        # Инициализация для v2
        pass

    def _get_transcription_pb2(self):
        # Вернуть v2 protobuf модуль
        pass

    def _transcribe_file(self, file_path: str) -> dict:
        # Реализация для v2
        pass

    def get_version(self) -> str:
        return "02"
```

#### 3. Создать Java клиент

```bash
# Создать agora-backend/src/main/java/ai/agorabackend/service/v2/TranscriptionClientService02.java
```

```java
@Service
public class TranscriptionClientService02 extends TranscriptionClientBase {

    private TranscriptionServiceGrpc.TranscriptionServiceBlockingStub blockingStub;

    @Override
    protected void initStub() {
        blockingStub = ai.agora.proto.v2.TranscriptionServiceGrpc.newBlockingStub(channel);
    }

    @Override
    public String getVersion() {
        return "02";
    }

    @Override
    public TranscriptionResult transcribeAudio(String audioFilePath) {
        // Реализация для v2
    }
}
```

#### 4. Обновить фасады

**Python** (`transcription_service.py`):
```python
def serve(port=50051, version='01'):
    if version == '01':
        service_impl = TranscriptionService01()
    elif version == '02':
        service_impl = TranscriptionService02()
    # ...
```

**Java** (`TranscriptionClientService.java`):
```java
@Autowired
private TranscriptionClientService02 clientService02;

private ITranscriptionClient getActiveClient() {
    switch (clientVersion) {
        case "01": return clientService01;
        case "02": return clientService02;
        default: return clientService01;
    }
}
```

## Преимущества архитектуры

### 1. Разделение ответственности
- **Интерфейс**: определяет контракт
- **Абстрактный класс**: содержит общую логику
- **Реализация**: специфичная логика для версии

### 2. Переиспользование кода
- Общая логика (работа с файлами, ошибки, логирование) в базовом классе
- Версии реализуют только специфичную логику

### 3. Легкость добавления новых версий
- Создать новую реализацию, наследуя базовый класс
- Минимальные изменения в существующем коде

### 4. Обратная совместимость
- Старые версии продолжают работать
- Клиенты могут выбирать версию

### 5. Тестируемость
- Легко мокировать интерфейсы
- Тестировать версии независимо

## Соглашения об именовании

- **Proto файлы**: `proto/v{N}/service_name.proto`
- **Proto package**: `service_name.v{N}`
- **Java package**: `ai.agora.proto.v{N}`
- **Python класс**: `ServiceName{NN}` (например, `TranscriptionService01`)
- **Java класс**: `ServiceName{NN}` (например, `TranscriptionClientService01`)
- **Версия**: двузначное число с ведущим нулем (`01`, `02`, ..., `10`, `11`, ...)

## Миграция между версиями

### Для клиентов

1. Обновить `application.properties`:
   ```properties
   transcription.client.version=02
   ```

2. Перезапустить приложение

### Для серверов

1. Запустить новую версию сервера на другом порту (опционально)
2. Обновить клиентов для использования новой версии
3. Остановить старую версию после миграции всех клиентов

## Best Practices

1. **Не изменяйте существующие версии** - создавайте новые версии для breaking changes
2. **Документируйте изменения** между версиями в CHANGELOG
3. **Поддерживайте минимум 2 версии** одновременно для плавной миграции
4. **Используйте семантическое версионирование** для proto файлов
5. **Тестируйте обратную совместимость** при добавлении новых версий
