from confluent_kafka.admin import AdminClient, NewTopic

class KafkaAdmin:
    """Kafka Admin class. Can create topics.

        Attributes:
            _conf (object): Configuration object
            _admin (AdminClient): AdminClient object
    """ 
    def __init__(self, conf):
        self._conf = conf
        self._admin = AdminClient(self._conf)

    def create_topic(self, topic, partitions=1, replication_factor=1):
        """Creates a topic

        Args:
            topic (str): Topic name
            partitions (int, optional): # Partitions. Defaults to 1.
            replication_factor (int, optional): Replication factor. Defaults to 1.

        Returns:
            [type]: [description]
        """        
        futures = self._admin.create_topics(
        [NewTopic(
            topic,
            num_partitions=partitions,
            replication_factor=replication_factor)
        ])

        return futures