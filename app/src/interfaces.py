import abc

class SenderInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'send') and 
                callable(subclass.send) and
                hasattr(subclass, 'create_topic') and 
                callable(subclass.create_topic) and
                hasattr(subclass, 'list_topics') and 
                callable(subclass.list_topics) and
                hasattr(subclass, 'flush') and 
                callable(subclass.flush) 
                or NotImplemented)

    @abc.abstractmethod
    def send(self, topic, msg, callback, sync):
        raise NotImplementedError
    
    @abc.abstractmethod
    def create_topic(self, topic):
        raise NotImplementedError

    @abc.abstractmethod
    def list_topics(self):
        raise NotImplementedError

    @abc.abstractmethod
    def flush(self):
        raise NotImplementedError
class ReceiverInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'receive') and 
                callable(subclass.receive) and 
                hasattr(subclass, 'subscribe') and 
                callable(subclass.subscribe) and 
                hasattr(subclass, 'close') and 
                callable(subclass.close)  
                or NotImplemented)

    @abc.abstractmethod
    def receive(self, timeout, callback):
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(self, topic):
        raise NotImplementedError
    
    @abc.abstractmethod
    def close(self):
        raise NotImplementedError