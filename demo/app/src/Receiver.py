import json
from src.kafka.KafkaConsumer import KafkaConsumer
from src.pubsub.PSSubscriber import PSSubscriber
from src.Message import Message

def process_res(*args):
    if len(args)==2: #Kafka
        res, _ = args
        if res.error():
            print("Error")
            return
        key = res.key().decode("utf-8")
        value = res.value().decode("utf-8")
        msg = Message(key=key, value=value)
        print(f"Received record ID {msg.key}")
    else: #PubSub
        res = args[0]
        msg = json.loads(res.data)
        msg = Message(key=msg["key"], value=msg["value"])
        print(f"Received record ID {msg.key}")
        res.ack()

class Receiver:
    def __init__(self, conf, _from):

        self._type = _from
        if self._type == "kafka":
            self._receiver = KafkaConsumer(conf)
        else:
            self._receiver = PSSubscriber(conf)

    def close(self):
        self._receiver.close()

    def subscribe(self, topic):
        self._receiver.subscribe(topic)

    def receive(self, timeout=1, callback=process_res):
        self._receiver.receive(timeout=timeout, callback=callback)