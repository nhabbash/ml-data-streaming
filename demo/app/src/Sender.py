import threading
import json
from .KafkaProducer import KafkaProducer
from .Publisher import Publisher

class Sender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self._sender = None
    
    def setup(self, config_file):
        with open(config_file, "r") as file:
            conf = json.load(file)
        
        type = config_file.split("/")[1]

        if type not in ["kafka", "pubsub"]:
            raise Exception("Only Kafka and PubSub are supported")
        
        if type == "kafka":
            self._sender = KafkaProducer(conf)
        else:
            self._sender = Publisher(conf)

    def stop(self):
        self.stop_event.set()

    def send(self, topic, key, msg, sync=False, callback=None):
        self._sender.send(topic=topic, key=key, msg=msg, sync=sync, callback=callback)