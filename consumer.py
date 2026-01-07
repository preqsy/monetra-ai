import json
from confluent_kafka import Consumer, KafkaError


class KafkaConsumer:
    def __init__(self, topic: str, group_id: str = "monetra-ai") -> None:
        self.consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": group_id,
                "auto.offset.reset": "earliest",
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
