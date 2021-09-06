import json
from confluent_kafka import Producer

from src.kafka.KafkaAdmin import KafkaAdmin
from src.interfaces import SenderInterface

class KafkaProducer(SenderInterface):
    """Kafka Producer for producing messages to a Kafka broker.

        Attributes:
            _prod_conf (object): Producer configuration object
            _admin_con (obj): Admin configuration object, needed to create topics
            _producer (Producer): Producer object
    """         
    def __init__(self, conf):
        self._prod_conf = conf
        self._admin_conf = None
        self._producer = Producer(self._prod_conf)

    def send(self, topic, msg, callback=None):
        """Sends message to topic

        Args:
            topic (str): Topic
            msg (Message): Message object
            callback (fn(msg, err), optional): Delivery acknowledgment callback. Defaults to None.

        Raises:
            Exception: Topic does not exist
        """        
        if topic not in self.list_topics():
            raise Exception(f"Topic '{topic}' does not exist, aborting send")
        
        self._producer.produce(topic, 
                                key=msg.key, 
                                value=msg.value,
                                on_delivery=callback)
        self._producer.poll(0)

    def flush(self):
        """Wait for all messages in the Producer queue to be delivered.
        """
        self._producer.flush(1.0)

    def create_topic(self, topic):
        """Creates topic

        Args:
            topic (str): Topic name

        Raises:
            Exception: No KafkaAdmin configuration provided

        Yields:
            err, topic: Yields error if there is and a Topic future
        """        
        if self._admin_conf:
            admin = KafkaAdmin(self._admin_conf)
            futures = admin.create_topic(topic)
                    
            for topic, f in futures.items():
                try:
                    f.result()
                    yield None, topic
                except Exception as e:
                    yield e, topic
        else:
            raise Exception("No KafkaAdmin configuration to create a topic")

    def list_topics(self):
        """List topics

        Returns:
            list: Topics
        """        
        cluster_metadata = self._producer.list_topics()
        topics = cluster_metadata.topics.keys()
        return topics

    def _init_admin_config(self, conf):
        """Initialize Kafka Admin config

        Args:
            conf (object): Configuration object
        """
        self._admin_conf = conf

    def delete_topic(self, topic):
        pass
    