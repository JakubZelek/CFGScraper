import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient


KAFKA_GROUP = "cfg_group"
AUTO_OFFSET_RESET = "earliest"

class KafkaProducerManager:
    def __init__(self, kafka_broker: str):
        self.admin_client = KafkaAdminClient(bootstrap_servers=kafka_broker)
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )


    async def push_to_the_topic(self, topic: str, message: dict):
        self.producer.send(topic, message)

    async def flush(self):
        self.producer.flush()

class KafkaConsumerManager:
    def __init__(self, kafka_broker: str, kafka_topic: str, group_id: str = KAFKA_GROUP):
        self.consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=kafka_broker,
            auto_offset_reset=AUTO_OFFSET_RESET,
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

    def get_messages(self):
        for message in self.consumer:
            yield message.value
