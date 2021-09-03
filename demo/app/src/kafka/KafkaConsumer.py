from confluent_kafka import Consumer
from src.interfaces import ReceiverInterface

class KafkaConsumer(ReceiverInterface):
    def __init__(self, conf):
        self._conf = conf
        self._consumer = Consumer(conf)

    def subscribe(self, topic, callback=None):
        if not isinstance(topic, list):
            topic = [topic]
        self._consumer.subscribe(topic)

    def unsubscribe(self, topic, callback=None):
        pass

    def receive(self, callback, timeout=None):
        try:
            res = None
            while True:
                res = self._consumer.poll(timeout=timeout)
                if res is None:
                    continue
                callback(res, 0)
        except Exception as e:
            print(e)