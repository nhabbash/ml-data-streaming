
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaError
import json

class KafkaAdmin:
    def __init__(self, conf):
        self._conf = conf
        self._admin = AdminClient(self._conf)

    def create_topic(self, topic, partitions=1, replication_factor=1):
        futures = self._admin.create_topics(
        [NewTopic(
            topic,
            num_partitions=partitions,
            replication_factor=replication_factor)
        ])

        return futures