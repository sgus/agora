package ai.agorabackend.service.base;

import ai.agorabackend.service.TranscriptionClientService.TranscriptionResult;

/**
 * Интерфейс для клиента транскрипции
 */
public interface ITranscriptionClient {

    /**
     * Отправляет аудио файл на транскрипцию
     *
     * @param audioFilePath путь к аудио файлу
     * @return результат транскрипции
     */
    TranscriptionResult transcribeAudio(String audioFilePath);

    /**
     * Возвращает версию клиента
     *
     * @return версия клиента
     */
    String getVersion();

    /**
     * Инициализация клиента
     */
    void init();

    /**
     * Закрытие соединения
     */
    void shutdown();
}
