import functools
import json
from src.Message import Message

def on_delivery(func):
    """Process responses from either Kafka or PubSub to the same format
    """    
    @functools.wraps(func)
    def wrapper_decorator(*args):
        err, msg_id = None, None
        if len(args)==2: # Kafka
            err, msg = args
            msg_id = msg.key().decode('utf-8')
        else: # PubSub
            future = args[0]
            try:
                msg_id = future.result()
            except Exception as e:
                err = e
        
        func(err, msg_id)

    return wrapper_decorator

def on_receive(func):
    """Process responses from either Kafka or PubSub to the same format (Message object)
    """    
    @functools.wraps(func)
    def wrapper_decorator(*args):
        err, msg = None, None
        if len(args)==2: # Kafka
            res, _ = args
            if res.error():
                err = res.error()
                return err, msg
                
            msg = Message.from_kafka(res)
        else: #PubSub
            # In PubSub errors are handled in the future
            res = args[0]

            msg = Message.from_PS(res)
            res.ack()

        func(err, msg)
    return wrapper_decorator