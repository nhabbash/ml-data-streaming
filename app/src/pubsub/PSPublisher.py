from google.cloud import pubsub_v1
from concurrent import futures

from src.interfaces import SenderInterface

class PSPublisher(SenderInterface):
    """PubSub Publisher for sending messages to a PubSub broker.

    Attributes:
        _conf (object): Configuration object
        _publisher (PublisherClient): Publisher object
        _project_id (str): GC compliant Project ID
        _project_path (str): GC compliant Project path
        futures (list): List of futures from sent messages
    """
    def __init__(self, conf):
        self._conf = conf
        self._project_id = self._conf['project_id']
        self._project_path = f"projects/{self._project_id}"

        self._publisher = pubsub_v1.PublisherClient()
        self.futures = []

    def send(self, topic, msg, callback=None):
        """Sends messages to a PubSub topic.

        Args:
            topic (str): Topic name
            msg (Message): Message object
            callback (fn(*args), optional): Callback called on successful delivery. Defaults to None.

        Raises:
            Exception: Topic does not exist
        """        
        topic_path = self._publisher.topic_path(self._project_id, topic)
        
        if topic_path not in self.list_topics():
            raise Exception(f"Topic '{topic}' does not exist, aborting send")
        
        future = self._publisher.publish(topic_path, msg.toJSON().encode("utf8"))
        future.add_done_callback(callback)

        self.futures.append(future)

    def flush(self):
        """Wait for all messages in the Publisher queue to be delivered.
        """    
        futures.wait(self.futures, return_when=futures.ALL_COMPLETED)

    def list_topics(self):
        """Lists topic in broker

        Returns:
            (list): List of all topics
        """        
        return [t.name for t in self._publisher.list_topics(project=self._project_path)]

    def create_topic(self, topic):
        """Creates topic

        Args:
            topic (str): Topic name

        Yields:
            err (error), topic_path (str): Error and topic path on topic creation
        """        
        topic_path = self._publisher.topic_path(self._project_id, topic)
        try:
            topic = self._publisher.create_topic(name=topic_path)
            yield None, topic.name
        except Exception as e:
            yield e, topic_path
    
    def delete_topic(self, topic):
        pass

    def list_subscriptions_in_topic(self, topic):
        pass