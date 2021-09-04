from google.cloud import pubsub_v1
import uuid

from src.interfaces import ReceiverInterface

class PSSubscriber(ReceiverInterface):
    def __init__(self, conf):
        self._conf = conf
        self._project_id = self._conf['project_id']
        self._project_path = f"projects/{self._project_id}"
        self._sub_id = self._conf['subscriber_id_prefix']+"-"+uuid.uuid4().hex[:4]
        self._subscriber = pubsub_v1.SubscriberClient()

    def subscribe(self, topic, type="pull", callback=None):
        topic_path = self._subscriber.topic_path(self._project_id, topic)
        self.subscription_path = self._subscriber.subscription_path(self._project_id, self._sub_id)

        push_config = None
        if type=="push":
            self.push_config = pubsub_v1.types.PushConfig(push_endpoint=self._conf["endpoint"])

        self._subscriber.create_subscription(name=self.subscription_path, topic=topic_path, push_config=push_config)

    def unsubscribe(self, topic, callback=None):
        pass

    def close(self):
        self._subscriber.close()
    
    def receive(self, callback, timeout=None):
        futures = self._subscriber.subscribe(subscription=self.subscription_path, callback=callback)
        with self._subscriber:
            try:
                futures.result(timeout=None)
            except Exception as e:
                print(e)
                futures.cancel()
                futures.result()


