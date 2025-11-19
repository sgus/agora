# План удаления Legacy Proto файла

## Файл для удаления
- `proto/transcription.proto` (legacy, deprecated)

## Проверка перед удалением

### ✅ Проверено - НЕ используется:
1. **Python проект** - обновлен на `proto/v1/transcription.proto`
2. **Java backend код** - использует только `ai.agora.proto.v1.*`
3. **Активные сервисы** - все используют версионированные proto

### ⚠️ Что будет затронуто:
1. **Java build** - перестанет генерировать классы `ai.agora.proto.*` (legacy package)
   - Это нормально, т.к. эти классы не используются в коде
2. **Документация** - нужно обновить упоминания legacy файла

## Шаги для удаления

### 1. Удалить legacy proto файл
```bash
rm proto/transcription.proto
```

### 2. Удалить legacy сгенерированные файлы в Python
```bash
rm agora-python/generated/transcription_pb2.py
rm agora-python/generated/transcription_pb2_grpc.py
```

### 3. Обновить документацию

**proto/README.md:**
- Удалить упоминание `transcription.proto` из списка файлов
- Обновить раздел "Структура"

**proto/VERSIONING.md:**
- Удалить строку `└── transcription.proto # Legacy (deprecated)`
- Обновить примеры структуры

**SETUP.md:**
- Удалить или обновить устаревшие примеры генерации proto (строки 162-166)

### 4. Пересобрать проекты

**Java backend:**
```bash
cd agora-backend
./gradlew clean build
```

**Python:**
```bash
cd agora-python
generate_proto.bat
```

### 5. Проверить, что все работает

**Запустить Python сервер:**
```bash
cd agora-python
python services/transcription_service.py
```

**Запустить Java backend:**
```bash
cd agora-backend
./gradlew bootRun
```

## Откат (если что-то пойдет не так)

Legacy файл сохранен в git истории. Для отката:
```bash
git checkout HEAD -- proto/transcription.proto
```

## Преимущества удаления

1. ✅ Чистота кодовой базы - нет deprecated кода
2. ✅ Меньше путаницы - один источник истины (v1)
3. ✅ Быстрее сборка - меньше файлов для генерации
4. ✅ Ясность архитектуры - только версионированные proto

## Риски

⚠️ **Минимальные риски:**
- Все активные компоненты используют v1
- Legacy классы не используются в коде
- Можно легко откатить через git

## Решение

**Рекомендуется удалить сейчас**, так как:
- Файл помечен как deprecated
- Не используется ни в одном активном коде
- Проект полностью мигрирован на версионированную архитектуру
