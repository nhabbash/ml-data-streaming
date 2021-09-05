from src.kafka.KafkaConsumer import KafkaConsumer
from src.pubsub.PSSubscriber import PSSubscriber
from src.decorators import on_receive

@on_receive
def receive_cb(err, msg):
    """Receive callback called when a message is receive, containing the formatted message

    Args:
        err (Exception): Error if there was any
        msg (Message): Received message
    """    
    if err:
        print(f"Error while receiving the message: {err}")
    else:
        print(f"Received record ID {msg.key}")
class Receiver:
    """Generic Receiver class. Receives messages from whatever message broker it's been configurated with.

        Attributes:
            _type (str): Message Broker type
            _receiver (ReceiverInterface): Receiver object
    """     
    def __init__(self, conf, _from):
        self._type = _from
        if self._type == "kafka":
            self._receiver = KafkaConsumer(conf)
        else:
            self._receiver = PSSubscriber(conf)

    def close(self):
        """Closes receiver
        """        
        self._receiver.close()

    def subscribe(self, topic):
        """Subscribes to topic

        Args:
            topic (str): Topic name
        """        
        self._receiver.subscribe(topic)

    def receive(self, timeout=None, callback=receive_cb):
        """Listen to messages on the subscribed topic

        Args:
            timeout (float, optional): Maximum time to block waiting for message, event or callback. Defaults to 1.
            callback (fn(*args), optional): Message handling callback. Defaults to process_res.
        """
        try:
            self._receiver.receive(timeout=timeout, callback=callback)
        except Exception as e:
            print(e)