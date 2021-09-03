from google.cloud import pubsub_v1
from concurrent import futures

from src.interfaces import SenderInterface

class PSPublisher(SenderInterface):
    def __init__(self, conf):
        self._conf = conf
        self._project_id = self._conf['project_id']
        self._project_path = f"projects/{self._project_id}"

        self._publisher = pubsub_v1.PublisherClient()
        self.futures = []

    def send(self, topic, msg, callback=None):
        topic_path = self._publisher.topic_path(self._project_id, topic)
        
        if topic_path not in self.list_topics():
            raise Exception(f"Topic '{topic}' does not exist, aborting send")
        
        future = self._publisher.publish(topic_path, msg.toJSON().encode("utf8"))
        future.add_done_callback(callback)

        self.futures.append(future)

    def flush(self):
        futures.wait(self.futures, return_when=futures.ALL_COMPLETED)

    def list_topics(self):
        return [t.name for t in self._publisher.list_topics(project=self._project_path)]

    def create_topic(self, topic):
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