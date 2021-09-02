from confluent_kafka import Consumer, TopicPartition

class KafkaConsumer:
    def __init__(self, conf):
        self._consumer = Consumer(conf)

    def subscribe(self, topic):
        if not isinstance(topic, list):
            raise Exception("Topic to subscribe to must be a list")
        self._consumer.subscribe(topic)

    def subscribe_to_partition(self, topic_partition):
        if not isinstance(topic_partition, list):
            raise Exception("Topic partition to subscribe to must be a list")
        self._consumer.assign([TopicPartition(topic_partition, 0)])

    def consume(self, timeout):
        try:
            while True:
                msg = self._consumer.poll(timeout)
                if msg is None:
                    continue
                if msg.error():
                    print("Consumer error: {}".format(msg.error()))
                    continue
                yield msg
        except KeyboardInterrupt:
            pass
        finally:
            self._consumer.close()

    def consume(self, timeout=1, session_max=-1):
        try:
            session = 0
            while True:
                msg = self._consumer.poll(timeout)
                if msg is None:
                    session += 1
                    if session_max !=-1 and session > session_max:
                        break
                    continue
                if msg.error():
                    print("Consumer error: {}".format(msg.error()))
                    continue
                yield msg
            self._consumer.close() 
        except KeyboardInterrupt:
            pass
        finally:
            self._consumer.close()

    def receive(self, timeout, session_max):
        for msg in self.consume(timeout, session_max):
            print(msg.key(), msg.value())