package ai.agorabackend.service.base;

import ai.agorabackend.service.TranscriptionClientService.TranscriptionResult;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;

/**
 * Абстрактный базовый класс для клиента транскрипции.
 * Содержит общую логику подключения к gRPC серверу и работы с файлами.
 */
public abstract class TranscriptionClientBase implements ITranscriptionClient {

    private static final Logger logger = LoggerFactory.getLogger(TranscriptionClientBase.class);

    @Value("${transcription.grpc.host:localhost}")
    protected String grpcHost;

    @Value("${transcription.grpc.port:50051}")
    protected int grpcPort;

    protected ManagedChannel channel;

    /**
     * Инициализация клиента
     */
    @PostConstruct
    public void init() {
        logger.info("Инициализация {}...", this.getClass().getSimpleName());
        logger.info("Подключение к gRPC серверу: {}:{}", grpcHost, grpcPort);

        // Устанавливаем максимальный размер сообщений в 200 МБ
        int maxMessageSize = 200 * 1024 * 1024; // 200 MB

        channel = ManagedChannelBuilder.forAddress(grpcHost, grpcPort)
                .usePlaintext()
                .maxInboundMessageSize(maxMessageSize)
                .maxInboundMetadataSize(maxMessageSize)
                .build();

        initStub();

        logger.info("✓ {} инициализирован (версия {})", this.getClass().getSimpleName(), getVersion());
    }

    /**
     * Инициализация stub для конкретной версии.
     * Должен быть реализован в наследниках.
     */
    protected abstract void initStub();

    /**
     * Закрытие gRPC канала
     */
    @PreDestroy
    public void shutdown() {
        logger.info("Закрытие gRPC канала...");
        try {
            if (channel != null) {
                channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
            }
        } catch (InterruptedException e) {
            logger.error("Ошибка при закрытии канала", e);
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Читает аудио файл в байты
     *
     * @param audioFilePath путь к файлу
     * @return байты файла
     * @throws IOException если файл не найден или ошибка чтения
     */
    protected byte[] readAudioFile(String audioFilePath) throws IOException {
        Path path = Path.of(audioFilePath);

        if (!Files.exists(path)) {
            throw new IOException("Файл не найден: " + audioFilePath);
        }

        byte[] audioData = Files.readAllBytes(path);
        logger.info("Размер файла: {:.2f} MB", audioData.length / 1024.0 / 1024.0);

        return audioData;
    }

    /**
     * Логирует результат транскрипции
     *
     * @param result результат транскрипции
     * @param elapsedTime время выполнения запроса
     */
    protected void logTranscriptionResult(TranscriptionResult result, long elapsedTime) {
        if (result.isSuccess()) {
            logger.info("✓ Транскрипция успешна!");
            logger.info("  Время обработки: {:.2f}s", result.getProcessingTime());
            logger.info("  Длительность аудио: {:.2f}s", result.getAudioDuration());
            logger.info("  Скорость: {:.1f}x реального времени", result.getSpeedFactor());
            logger.info("  Слов: {}", result.getWordCount());
            logger.info("  Символов: {}", result.getCharCount());
            logger.info("  Время запроса: {}ms", elapsedTime);
        } else {
            logger.error("❌ Ошибка транскрипции: {}", result.getErrorMessage());
        }
    }

    /**
     * Создает результат с ошибкой
     *
     * @param errorMessage сообщение об ошибке
     * @return результат с ошибкой
     */
    protected TranscriptionResult createErrorResult(String errorMessage) {
        return new TranscriptionResult(
                false,
                null,
                errorMessage,
                0.0,
                0.0,
                0,
                0,
                0.0
        );
    }
}
