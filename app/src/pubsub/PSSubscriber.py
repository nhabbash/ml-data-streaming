from google.cloud import pubsub_v1
import uuid

from src.interfaces import ReceiverInterface

class PSSubscriber(ReceiverInterface):
    """PubSub Subscriber for receiving messages from a PubSub broker.

    Attributes:
        _conf (object): Configuration object
        _subscriber (SubscriberClient): Subscriber object
        _project_id (str): GC compliant Project ID
        _project_path (str): GC compliant Project path
        _sub_id (str): GC compliant Subscription ID
    """
    def __init__(self, conf):
        self._conf = conf
        self._project_id = self._conf['project_id']
        self._project_path = f"projects/{self._project_id}"
        self._sub_id = self._conf['subscriber_id_prefix']+"-"+uuid.uuid4().hex[:4]
        self._subscriber = pubsub_v1.SubscriberClient()
        self.futures = []

    def subscribe(self, topic, type="pull", callback=None):
        """Subscribes to topic

        Args:
            topic (str): Topic name
            type (str, optional): Subscription type. Defaults to "pull".
            callback (fn(*args), optional): Callback to be called on success. Defaults to None.
        """        
        topic_path = self._subscriber.topic_path(self._project_id, topic)
        self.subscription_path = self._subscriber.subscription_path(self._project_id, self._sub_id)

        push_config = None
        if type=="push":
            self.push_config = pubsub_v1.types.PushConfig(push_endpoint=self._conf["endpoint"])

        self._subscriber.create_subscription(name=self.subscription_path, topic=topic_path, push_config=push_config)

    def close(self):
        """Close the underlying channel to release socket resources.
        """
        self._subscriber.close()
    
    def receive(self, callback, timeout=None):
        """Consumes message from PubSub broker from the subscribed topic

        Args:
            callback (fn(*args)): Message processing callback
            timeout (float, optional): Maximum time to block waiting for message, event or callback. Defaults to None.
        """
        
        future = self._subscriber.subscribe(subscription=self.subscription_path, callback=callback)
        #self.futures.append(future)
        try: # TODO: delegate error handling to Receiver.receive, move result() to a flush method
            future.result(timeout=timeout)
        except Exception as e:
            print(e)
            future.cancel()
            future.result()

    def unsubscribe(self, topic, callback=None):
        pass

