import json
import logging
import tempfile
from base64 import b64decode
from confluent_kafka import Consumer, KafkaError
from config import settings


if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

logger = logging.getLogger("consumer")


def write_temp_file(b64_content):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(b64decode(b64_content))
    tmp.flush()
    return tmp.name


ca_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_PEM)
cert_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_SERVICE_CERT)
key_path = write_temp_file(settings.KAFKA_CONFIG.KAFKA_SERVICE_KEY)

kafka_config = {
    "bootstrap.servers": "localhost:9092",
    "auto.offset.reset": "latest",  # Changed to 'latest' to only consume new messages
    "group.id": settings.KAFKA_CONFIG.KAFKA_GROUP_ID,
    "enable.auto.commit": True,
    "auto.commit.interval.ms": 5000,
}

if settings.ENVIRONMENT == "prod":
    kafka_config["bootstrap.servers"] = settings.KAFKA_CONFIG.KAFKA_URL
    kafka_config["security.protocol"] = "SSL"
    kafka_config["ssl.ca.location"] = ca_path
    kafka_config["ssl.certificate.location"] = cert_path
    kafka_config["ssl.key.location"] = key_path

logger.info("Kafka config loaded for environment=%s", settings.ENVIRONMENT)


class KafkaConsumer:
    def __init__(
        self,
        topic: str,
    ) -> None:
        self.topic = topic
        self.consumer = Consumer(
            {**kafka_config, "group.id": settings.KAFKA_CONFIG.KAFKA_GROUP_ID}
        )
        self.consumer.subscribe([topic])
        logger.info(
            "Subscribed to topic=%s group_id=%s",
            topic,
            settings.KAFKA_CONFIG.KAFKA_GROUP_ID,
        )

    def consume_message(self, handler):
        logger.info("Listening to topic=%s", self.topic)
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.warning("Consumer error: %s", msg.error())
                        continue

                try:
                    event = json.loads(msg.value())
                    logger.info(
                        "Message received topic=%s partition=%s offset=%s",
                        msg.topic(),
                        msg.partition(),
                        msg.offset(),
                    )
                    logger.debug("Event payload: %s", event)

                    # Process the message
                    handler(event)

                    # Manually commit only after successful processing
                    self.consumer.commit(msg)
                    logger.debug("Committed offset=%s", msg.offset())

                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to decode JSON from offset %s: %s", msg.offset(), e
                    )
                    # Commit anyway to skip bad message
                    self.consumer.commit(msg)

                except Exception as e:
                    logger.error("Handler failed for offset %s: %s", msg.offset(), e)
                    logger.exception("Full traceback:")
                    # Don't commit - message will be reprocessed on restart

        except KeyboardInterrupt:
            logger.info("Consumer interrupted")

        except Exception as e:
            logger.exception("Kafka exception")
        finally:
            self.consumer.close()
            logger.info("Consumer closed")
