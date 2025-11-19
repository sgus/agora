@echo off
REM Скрипт для генерации Python gRPC кода из proto файлов

echo ========================================
echo Генерация Python gRPC кода из proto
echo ========================================

REM Создаем директорию для сгенерированных файлов
if not exist "generated\v1" mkdir generated\v1

REM Создаем __init__.py файлы
echo. > generated\__init__.py
echo. > generated\v1\__init__.py

echo.
echo [1/2] Генерация transcription.proto...
python -m grpc_tools.protoc -I..\proto --python_out=generated --grpc_python_out=generated ..\proto\v1\transcription.proto

echo [2/2] Генерация audio_service.proto...
python -m grpc_tools.protoc -I..\proto --python_out=generated --grpc_python_out=generated ..\proto\v1\audio_service.proto

echo.
echo [3/3] Исправление импортов...
REM Исправляем импорты в сгенерированных файлах
powershell -Command "(Get-Content generated\v1\audio_service_pb2_grpc.py) -replace 'from v1 import audio_service_pb2', 'from generated.v1 import audio_service_pb2' | Set-Content generated\v1\audio_service_pb2_grpc.py"
powershell -Command "(Get-Content generated\v1\transcription_pb2_grpc.py) -replace 'from v1 import transcription_pb2', 'from generated.v1 import transcription_pb2' | Set-Content generated\v1\transcription_pb2_grpc.py"

echo.
echo ========================================
echo Генерация завершена!
echo ========================================
echo.
echo Сгенерированные файлы:
dir /B generated\v1\*.py

echo.
pause
