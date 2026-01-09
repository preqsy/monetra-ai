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


ca_path = write_temp_file(settings.KAFKA_PEM)
cert_path = write_temp_file(settings.KAFKA_SERVICE_CERT)
key_path = write_temp_file(settings.KAFKA_SERVICE_KEY)


class KafkaConsumer:
    def __init__(self, topic: str, group_id: str = "monetra-ai") -> None:
        self.consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_URL,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
                "security.protocol": "SSL",
                "ssl.ca.location": ca_path,
                "ssl.certificate.location": cert_path,
                "ssl.key.location": key_path,
            }
        )
        self.consumer.subscribe([topic])  # <-- subscribe to topic

    def consume_message(self, handler):
        print(f"listening.....")
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
