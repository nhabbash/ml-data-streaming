from confluent_kafka import Consumer
from src.interfaces import ReceiverInterface

class KafkaConsumer(ReceiverInterface):
    """Kafka Consumer for consuming messages from a Kafka broker.

    Attributes:
        _conf (object): Configuration object
        _consumer (Consumer): Consumer object
    """ 
    def __init__(self, conf):
        self._conf = conf
        self._consumer = Consumer(conf)

    def subscribe(self, topic, callback=None):
        """Subscribe to a topic

        Args:
            topic (str): Topic name
            callback (fn(*args), optional): Callback to be called on_assign of topic partition. Defaults to None.
        """        
        if not isinstance(topic, list):
            topic = [topic]
        self._consumer.subscribe(topic)

    def close(self):
        """Closes consumer connection.
        """        
        self._consumer.close()

    def receive(self, callback, timeout=None):
        """Consumes message from Kafka broker from the subscribed topic

        Args:
            callback (fn(*args)): Message processing callback
            timeout (float, optional): Maximum time to block waiting for message, event or callback. Defaults to None.
        """        
        res = None
        while True:
            res = self._consumer.poll(timeout=timeout)
            if res is None:
                continue
            callback(res, 0) #TODO: see config rd_kafka_conf_set_consume_cb()

    def unsubscribe(self, topic, callback=None):
        pass