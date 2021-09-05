from src.kafka.KafkaProducer import KafkaProducer
from src.pubsub.PSPublisher import PSPublisher
from src.decorators import on_delivery

@on_delivery
def send_cb(err, msg_id):
    """Delivery report callback called on successful or failed delivery of msg

    Args:
        err (Exception): Error if there was any
        msg_id (str): ID of the message sent
    """
    if err is None:
        print(f"Produced record ID {msg_id}")
    else:
        print(f"Failed to deliver message: {err}")

class Sender:
    """Generic Sender class. Sends messages to whatever message broker it's been configurated with.

        Attributes:
            _type (str): Message Broker target
            _sender (SenderInterface): Sender object
    """          
    def __init__(self, conf, to):
        self._type = to
        if self._type == "kafka":
            self._sender = KafkaProducer(conf)
        else:
            self._sender = PSPublisher(conf)

    def flush(self):
        """Flushes any messages still on-hold before closing
        """        
        self._sender.flush()

    def send(self, topic, msg, callback=send_cb):
        """Sends a message to a specified topic.

        Args:
            topic (str): Topic
            msg (Message): Message instance
            callback (optional): Delivery callback. Defaults to None.
        """ 
        try:
            self._sender.send(topic=topic, msg=msg, callback=callback)
        except Exception as e:
            print(e)

    def create_topic(self, topic):
        """Creates topic if it doesn't exist already.

        Args:
            topic (str): Topic
        """        
        for res, t in self._sender.create_topic(topic):
            if res != None:
                print(f"Failed to create topic {t}: {res}")
            else:
                print(f"Created topic '{t}'")

    def list_topics(self):
        """Lists all topic present in the message broker.
        """        
        print("Listing topics: ")
        for t in self._sender.list_topics():
            print(t)