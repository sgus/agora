package ai.agorabackend.service;

import ai.agorabackend.service.base.ITranscriptionClient;
import ai.agorabackend.service.v1.TranscriptionClientService01;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

/**
 * Фасад для работы с версионированными клиентами транскрипции.
 * Делегирует вызовы к конкретной версии клиента.
 *
 * ПРИМЕЧАНИЕ: Для работы требуется сгенерировать proto классы:
 * ./gradlew :agora-backend:generateProto
 */
@Service
@Primary
public class TranscriptionClientService {
    
    private static final Logger logger = LoggerFactory.getLogger(TranscriptionClientService.class);

    @Value("${transcription.client.version:01}")
    private String clientVersion;

    @Autowired
    private TranscriptionClientService01 clientService01;

    /**
     * Получает активный клиент в зависимости от настроенной версии
     *
     * @return активный клиент транскрипции
     */
    private ITranscriptionClient getActiveClient() {
        switch (clientVersion) {
            case "01":
                return clientService01;
            default:
                logger.warn("Неизвестная версия клиента: {}, используется версия 01", clientVersion);
                return clientService01;
        }
    }
    
    /**
     * Отправляет аудио файл на транскрипцию
     *
     * @param audioFilePath путь к аудио файлу
     * @return результат транскрипции
     */
    public TranscriptionResult transcribeAudio(String audioFilePath) {
        ITranscriptionClient client = getActiveClient();
        logger.info("Используется клиент версии: {}", client.getVersion());
        return client.transcribeAudio(audioFilePath);
    }
    
    /**
     * Результат транскрипции
     */
    public static class TranscriptionResult {
        private final boolean success;
        private final String transcript;
        private final String errorMessage;
        private final double processingTime;
        private final double audioDuration;
        private final int wordCount;
        private final int charCount;
        private final double speedFactor;
        
        public TranscriptionResult(boolean success, String transcript, String errorMessage,
                                   double processingTime, double audioDuration,
                                   int wordCount, int charCount, double speedFactor) {
            this.success = success;
            this.transcript = transcript;
            this.errorMessage = errorMessage;
            this.processingTime = processingTime;
            this.audioDuration = audioDuration;
            this.wordCount = wordCount;
            this.charCount = charCount;
            this.speedFactor = speedFactor;
        }
        
        public boolean isSuccess() { return success; }
        public String getTranscript() { return transcript; }
        public String getErrorMessage() { return errorMessage; }
        public double getProcessingTime() { return processingTime; }
        public double getAudioDuration() { return audioDuration; }
        public int getWordCount() { return wordCount; }
        public int getCharCount() { return charCount; }
        public double getSpeedFactor() { return speedFactor; }
        
        @Override
        public String toString() {
            if (success) {
                return String.format("TranscriptionResult{success=true, words=%d, chars=%d, speed=%.1fx, time=%.2fs}",
                        wordCount, charCount, speedFactor, processingTime);
            } else {
                return String.format("TranscriptionResult{success=false, error='%s'}", errorMessage);
            }
        }
    }
}
