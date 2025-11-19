package ai.agorabackend;

import ai.agorabackend.service.TranscriptionClientService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@SpringBootApplication
public class AgoraBackendApplication {

    private static final Logger logger = LoggerFactory.getLogger(AgoraBackendApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(AgoraBackendApplication.class, args);
    }

    /**
     * Выполняется при старте приложения
     * Отправляет sample.wav на транскрипцию
     */
    @Bean
    public CommandLineRunner transcribeOnStartup(TranscriptionClientService transcriptionService) {
        return args -> {
            logger.info("=".repeat(80));
            logger.info("Запуск транскрипции sample.wav при старте приложения...");
            logger.info("=".repeat(80));

            // Путь к sample.wav в src/main/java/ai/agorabackend
            String sampleWavPath = "agora-backend/src/main/java/ai/agorabackend/sample.wav";
            Path path = Paths.get(sampleWavPath);

            if (!Files.exists(path)) {
                logger.warn("⚠ Файл sample.wav не найден по пути: {}", sampleWavPath);
                logger.warn("  Пропускаем транскрипцию при старте.");
                logger.warn("  Убедитесь, что файл существует и путь указан правильно.");
                return;
            }

            try {
                logger.info("Найден файл: {}", path.toAbsolutePath());

                // Отправляем на транскрипцию
                TranscriptionClientService.TranscriptionResult result =
                        transcriptionService.transcribeAudio(path.toAbsolutePath().toString());

                // Выводим результат
                if (result.isSuccess()) {
                    logger.info("\n" + "=".repeat(80));
                    logger.info("РЕЗУЛЬТАТ ТРАНСКРИПЦИИ");
                    logger.info("=".repeat(80));
                    logger.info("\n{}", result.getTranscript());
                    logger.info("\n" + "=".repeat(80));
                    logger.info("Статистика:");
                    logger.info("  Слов: {}", result.getWordCount());
                    logger.info("  Символов: {}", result.getCharCount());
                    logger.info("  Длительность аудио: {:.2f}s", result.getAudioDuration());
                    logger.info("  Время обработки: {:.2f}s", result.getProcessingTime());
                    logger.info("  Скорость: {:.1f}x реального времени", result.getSpeedFactor());
                    logger.info("=".repeat(80));
                } else {
                    logger.error("❌ Транскрипция не удалась: {}", result.getErrorMessage());
                }

            } catch (Exception e) {
                logger.error("❌ Ошибка при транскрипции: {}", e.getMessage(), e);
            }
        };
    }

}
