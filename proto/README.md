# Proto Definitions

Это централизованное хранилище proto файлов для проекта Agora.

## Структура

- `transcription.proto` - определения для сервиса транскрипции аудио

## Использование

### Java (agora-backend)

Proto файлы автоматически компилируются в Java классы при сборке проекта:

```bash
./gradlew :agora-backend:build
```

Сгенерированные классы находятся в:
- `agora-backend/build/generated/source/proto/main/java/`
- `agora-backend/build/generated/source/proto/main/grpc/`

### Python (agora-python)

Для генерации Python классов используйте:

```bash
cd agora-python
generate_proto.bat
```

Сгенерированные файлы находятся в `agora-python/generated/v1/`

**Примечание:** Python проект использует версионированный proto файл `v1/transcription.proto`

## Добавление новых proto файлов

1. Создайте новый `.proto` файл в этой директории
2. Обновите скрипты генерации в соответствующих модулях
3. Пересоберите проекты

## Версионирование

Проект использует версионированную архитектуру для proto файлов и сервисов.

**Структура версий:**
- `v1/transcription.proto` - Версия 1 API
- `v2/transcription.proto` - Версия 2 API (будущая)
- `transcription.proto` - Legacy (deprecated, для обратной совместимости)

**Подробная документация:** См. [VERSIONING.md](VERSIONING.md) для полного описания архитектуры версионирования.
