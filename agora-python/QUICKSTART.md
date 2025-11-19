# Быстрый старт - AudioService

## Установка

```powershell
# 1. Активировать виртуальное окружение
.venv\Scripts\Activate.ps1

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Сгенерировать protobuf файлы (если еще не сделано)
.\generate_proto.bat
```

## Запуск сервера

```powershell
python services/audio_service.py
```

Сервер запустится на порту **50052**.

## Тестирование

```powershell
# Отправить тестовый аудио файл
python test_audio_client.py ml/audio.mp3
```

## Что делает сервис?

AudioService принимает аудио файлы и возвращает подтверждение:

**Запрос:** Аудио файл (например, `test.mp3`)

**Ответ:** `"файл test.mp3 получен"`

Файлы сохраняются в директории `uploads/` с timestamp.

## Примеры использования

### Унарный метод (весь файл сразу)
```powershell
python test_audio_client.py ml/audio.mp3 --method unary
```

### Стриминговый метод (по частям)
```powershell
python test_audio_client.py ml/audio.mp3 --method stream
```

### Другой сервер
```powershell
python test_audio_client.py ml/audio.mp3 --server localhost:50053
```

## Структура ответа

```json
{
  "message": "файл audio.mp3 получен",
  "success": true,
  "received_filename": "audio.mp3",
  "received_size": 1234567,
  "error_message": ""
}
```

## Поддерживаемые форматы

✅ MP3, WAV, M4A, FLAC, OGG, AAC

## Архитектура

Проект следует паттерну версионирования из `proto/VERSIONING.md`:

- **Proto:** `proto/v1/audio_service.proto`
- **Интерфейс:** `services/base/audio_service_interface.py`
- **Базовый класс:** `services/base/audio_service_base.py`
- **Реализация v01:** `services/v1/audio_service_01.py`
- **Сервер:** `services/audio_service.py`
