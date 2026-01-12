from base64 import b64decode
import json
import tempfile
from confluent_kafka import Consumer, KafkaError
from config import settings


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
    "auto.offset.reset": "earliest",
    "group.id": "monetra-ai",
}

if settings.ENVIRONMENT == "prod":
    kafka_config["bootstrap.servers"] = settings.KAFKA_CONFIG.KAFKA_URL
    kafka_config["security.protocol"] = "SSL"
    kafka_config["ssl.ca.location"] = ca_path
    kafka_config["ssl.certificate.location"] = cert_path
    kafka_config["ssl.key.location"] = key_path

print(f"Kafka config: {kafka_config}")


class KafkaConsumer:
    def __init__(self, topic: str, group_id: str = "monetra-ai") -> None:
        self.topic = topic
        self.consumer = Consumer(kafka_config)
        self.consumer.subscribe([topic])  # <-- subscribe to topic

    def consume_message(self, handler):
        print(f"listening to topic: {self.topic}.....")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        continue

                event = json.loads(msg.value())
                handler(event)

                self.consumer.commit(msg)  # <-- actually commit
        except KeyboardInterrupt:
            print("Consumer Interrupted")
        finally:
            self.consumer.close()
