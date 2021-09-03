import json
from confluent_kafka import Producer

from src.kafka.KafkaAdmin import KafkaAdmin
from src.interfaces import SenderInterface

class KafkaProducer(SenderInterface):
    def __init__(self, conf):
        self._prod_conf = conf
        self._admin_conf = None
        self._producer = Producer(self._prod_conf)

    def send(self, topic, msg, callback=None):
        if topic not in self.list_topics():
            raise Exception(f"Topic '{topic}' does not exist, aborting send")
        
        self._producer.produce(topic, 
                                key=msg.key, 
                                value=msg.value,
                                on_delivery=callback)
        self._producer.poll(0)

    def flush(self):
        self._producer.flush(1.0)

    def create_topic(self, topic):
        if self._admin_conf:
            admin = KafkaAdmin(self._admin_conf)
            futures = admin.create_topic(topic)
                    
            for topic, f in futures.items():
                try:
                    f.result()
                    yield None, topic
                except Exception as e:
                    yield e, topic

    def list_topics(self):
        cluster_metadata = self._producer.list_topics()
        topics = cluster_metadata.topics.keys()
        return topics

    def _init_admin_config(self, config_file):
        with open(config_file, "r") as file:
            conf = json.load(file)
        self._admin_conf = conf

    def delete_topic(self, topic):
        pass
    