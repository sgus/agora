# Установка и запуск transcribe.py

## Наши мучения и их решения 🔥

### Проблема 1: ModuleNotFoundError: No module named 'transformers'
**Ошибка:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Решение:**
Создали `requirements.txt` с необходимыми зависимостями.

---

### Проблема 2: Torch not compiled with CUDA enabled
**Ошибка:**
```
AssertionError: Torch not compiled with CUDA enabled
```

**Причина:**
По умолчанию `pip install torch` устанавливает CPU-версию PyTorch без поддержки CUDA.

**Решение:**
Нужно установить PyTorch с поддержкой CUDA вручную:

```powershell
pip uninstall torch torchvision torchaudio -y
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130
```

---

### Проблема 3: PySoundFile failed. Trying audioread instead
**Ошибка:**
```
UserWarning: PySoundFile failed. Trying audioread instead.
```

**Причина:**
Библиотека `soundfile` не была правильно установлена или отсутствовали необходимые зависимости.

**Решение:**
Добавили в requirements.txt:
- `soundfile>=0.12.0`
- `cffi>=1.15.0`
- `pysoundfile>=0.9.0`

И переустановили:
```powershell
pip install soundfile cffi pysoundfile --upgrade --force-reinstall
```

---

## Правильная последовательность установки

### Шаг 1: Создать виртуальное окружение
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Шаг 2: Установить PyTorch с CUDA
**ВАЖНО:** Сначала устанавливаем PyTorch с CUDA, потом остальные зависимости!

```powershell
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130
```

### Шаг 3: Установить остальные зависимости
```powershell
pip install -r requirements.txt
```

### Шаг 4: Проверить CUDA
```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else None}')"
```

Должно вывести:
```
CUDA available: True
CUDA version: 13.0
```

### Шаг 5: Запустить скрипт
```powershell
python .\ml\transcribe.py
```

---

## Требования к системе

- **GPU:** NVIDIA GPU с поддержкой CUDA
- **CUDA Toolkit:** версия 13.0 или совместимая
- **Драйверы NVIDIA:** последняя версия
- **Python:** 3.8+
- **Аудио файл:** `audio.mp3` в папке `ml/`

---

## Структура файлов

```
agora-python/
├── ml/
│   ├── transcribe.py       # Основной скрипт транскрипции
│   ├── audio.mp3           # Входной аудио файл
│   ├── requirements.txt    # Зависимости проекта
│   └── SETUP.md           # Этот файл
└── transcript.txt          # Выходной файл с транскрипцией
```

---

## Полезные команды

### Переустановить PyTorch с CUDA
```powershell
pip uninstall torch torchvision torchaudio -y
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130
```

### Переустановить soundfile
```powershell
pip install soundfile --upgrade --force-reinstall
```

### Проверить версии установленных пакетов
```powershell
pip list | Select-String "torch|transformers|librosa|soundfile"
```

---

## Troubleshooting

### Если CUDA недоступна после установки PyTorch
1. Проверьте, что у вас установлена NVIDIA GPU
2. Установите последние драйверы NVIDIA
3. Установите CUDA Toolkit 13.0
4. Перезагрузите компьютер
5. Переустановите PyTorch с правильным индексом

### Если ошибка при загрузке аудио
1. Убедитесь, что файл `audio.mp3` существует в папке `ml/`
2. Проверьте, что файл не поврежден
3. Попробуйте конвертировать аудио в WAV формат
4. Переустановите `soundfile` и `librosa`

---

## Примечания

- Скрипт требует CUDA и не будет работать на CPU (по дизайну)
- Модель Borealis загружается автоматически при первом запуске
- Транскрипция сохраняется в `transcript.txt` в корне проекта
