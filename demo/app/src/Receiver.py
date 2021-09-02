import threading
import json
import os
from .KafkaConsumer import KafkaConsumer
from .Subscriber import Subscriber

class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self._receiver = None
    
    def setup(self, config_file):
        with open(config_file, "r") as file:
            conf = json.load(file)
        
        type = config_file.split("/")[1]

        if type not in ["kafka", "pubsub"]:
            raise Exception("Only Kafka and PubSub are supported")
        
        if type == "kafka":
            self._receiver = KafkaConsumer(conf)
        else:
            self._receiver = Subscriber(conf)

    def stop(self):
        self.stop_event.set()

    def subscribe(self, topic):
        self._receiver.subscribe(topic)

    def receive(self, timeout=1, session_max=-1):
        self._receiver.receive(timeout, session_max)