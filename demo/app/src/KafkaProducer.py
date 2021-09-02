from confluent_kafka import Producer

def acked(err, msg):
    """Delivery report handler called on
    successful or failed delivery of msg
    """
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        print("Produced record to topic {} partition [{}] @ offset {}".format(msg.topic(), msg.partition(), msg.offset()))

class KafkaProducer: #TODO: add interface
    def __init__(self, conf):
        self._producer = Producer(conf)
    
    def send(self, topic, key, msg, callback=None, sync=False):
        if not self._check_topic_exists(topic):
            raise Exception(f"Topic '{topic}' does not exist")
        
        self._producer.produce(topic, 
                                key=key, 
                                value=msg,
                                on_delivery=acked)
        self._producer.poll(0)

        if sync:
            self._producer.flush(1.0)

    def _check_topic_exists(self, topic):
        cluster_metadata = self._producer.list_topics()
        topics = cluster_metadata.topics.keys()
        return topic in topics
