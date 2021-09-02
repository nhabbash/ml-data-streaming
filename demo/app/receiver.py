import argparse
import os, sys, json
from src.Receiver import Receiver

parser = argparse.ArgumentParser()
parser.add_argument(
    '--config',
    type=str,
    help='Path to a Kafka or PubSub config file',
    default=""
)
args = parser.parse_args()

def create_topic(conf, topic):
    from confluent_kafka.admin import AdminClient, NewTopic
    from confluent_kafka import KafkaError

    with open(conf, "r") as file:
            conf = json.load(file)

    admin = AdminClient(conf)

    fs = admin.create_topics(
        [NewTopic(
            topic,
            num_partitions=1,
            replication_factor=1)
        ])

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            # Continue if error code TOPIC_ALREADY_EXISTS, which may be true
            # Otherwise fail fast
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                print("Failed to create topic {}: {}".format(topic, e))
                sys.exit(1)

if __name__ == "__main__":

    receiver = Receiver()
    receiver.setup(config_file="config/kafka/consumer.json")
    pid = os.getpid()
    #create_topic("config/kafka/admin.json", "test")
    receiver.subscribe(["test"])
    receiver.receive()
