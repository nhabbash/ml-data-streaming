import abc

class SenderInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'send') and 
                callable(subclass.send) or 
                NotImplemented)

    @abc.abstractmethod
    def send(self, topic, msg, callback, sync):
        raise NotImplementedError
    
    @abc.abstractmethod
    def create_topic(self, topic):
        raise NotImplementedError

    @abc.abstractmethod
    def list_topics(self):
        raise NotImplementedError

class ReceiverInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'receive') and 
                callable(subclass.receive) or 
                NotImplemented)

    @abc.abstractmethod
    def receive(self, timeout, session_max):
        raise NotImplementedError