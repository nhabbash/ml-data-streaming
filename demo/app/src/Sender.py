import threading
import json
from src.kafka.KafkaProducer import KafkaProducer
from src.pubsub.PSPublisher import PSPublisher

def delivery_ack(*args):
    """Delivery report handler called on
    successful or failed delivery of msg
    """
    if len(args)==2: # Kafka
        err, msg = args
        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            print("Produced record to topic {} partition [{}] @ offset {}".format(msg.topic(), msg.partition(), msg.offset()))
    else: # PubSub
        future = args[0]
        try:
            msg_id = future.result()
            print("Produced record ID {}".format(msg_id))
        except Exception as e:
            print("Failed to deliver message: {}".format(e))


class Sender:
    def __init__(self, conf, to):
        self._type = to
        if self._type == "kafka":
            self._sender = KafkaProducer(conf)
        else:
            self._sender = PSPublisher(conf)

    def flush(self):
        self._sender.flush()

    def send(self, topic, msg, callback=None):
        self._sender.send(topic=topic, msg=msg, callback=callback)

    def create_topic(self, topic):
        for res, t in self._sender.create_topic(topic):
            if res != None:
                print(f"Failed to create topic {t}: {res}")
            else:
                print(f"Created topic '{t}'")

    def list_topics(self):
        print("Listing topics: ")
        for t in self._sender.list_topics():
            print(t)

    
