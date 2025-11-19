package ai.agorabackend.service.v1;

import ai.agorabackend.service.TranscriptionClientService.TranscriptionResult;
import ai.agorabackend.service.base.TranscriptionClientBase;
import ai.agora.proto.v1.AudioRequest;
import ai.agora.proto.v1.TranscriptionResponse;
import ai.agora.proto.v1.TranscriptionServiceGrpc;
import com.google.protobuf.ByteString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.nio.file.Path;

/**
 * Версия 01 клиента для отправки аудио на транскрипцию через gRPC.
 * Наследует TranscriptionClientBase и имплементирует ITranscriptionClient.
 */
@Service
public class TranscriptionClientService01 extends TranscriptionClientBase {

    private static final Logger logger = LoggerFactory.getLogger(TranscriptionClientService01.class);

    private TranscriptionServiceGrpc.TranscriptionServiceBlockingStub blockingStub;

    @Override
    protected void initStub() {
        blockingStub = TranscriptionServiceGrpc.newBlockingStub(channel);
        logger.info("✓ Blocking stub инициализирован для версии 01");
    }

    @Override
    public String getVersion() {
        return "01";
    }

    /**
     * Отправляет аудио файл на транскрипцию
     *
     * @param audioFilePath путь к аудио файлу
     * @return результат транскрипции
     */
    @Override
    public TranscriptionResult transcribeAudio(String audioFilePath) {
        logger.info("Отправка аудио на транскрипцию (v{}): {}", getVersion(), audioFilePath);

        try {
            // Читаем файл
            byte[] audioData = readAudioFile(audioFilePath);

            // Формируем запрос
            Path path = Path.of(audioFilePath);
            AudioRequest request = AudioRequest.newBuilder()
                    .setAudioData(ByteString.copyFrom(audioData))
                    .setFilename(path.getFileName().toString())
                    .setFormat("wav")
                    .setSampleRate(16000)
                    .build();

            logger.info("Отправка запроса на gRPC сервер...");
            long startTime = System.currentTimeMillis();

            // Отправляем запрос
            TranscriptionResponse response = blockingStub.transcribeAudio(request);

            long elapsedTime = System.currentTimeMillis() - startTime;

            // Формируем результат
            TranscriptionResult result;
            if (response.getSuccess()) {
                result = new TranscriptionResult(
                        true,
                        response.getTranscript(),
                        null,
                        response.getProcessingTime(),
                        response.getAudioDuration(),
                        response.getStats().getWordCount(),
                        response.getStats().getCharCount(),
                        response.getStats().getSpeedFactor()
                );
            } else {
                result = new TranscriptionResult(
                        false,
                        null,
                        response.getErrorMessage(),
                        response.getProcessingTime(),
                        0.0,
                        0,
                        0,
                        0.0
                );
            }

            logTranscriptionResult(result, elapsedTime);
            return result;

        } catch (Exception e) {
            logger.error("❌ Ошибка при отправке аудио: {}", e.getMessage(), e);
            return createErrorResult("Ошибка: " + e.getMessage());
        }
    }
}
