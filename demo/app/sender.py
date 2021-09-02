# Reads input from file
# Sends it to broker
# Waits responses
import argparse
import os
import json
from src.Sender import Sender
from src.Receiver import Receiver

parser = argparse.ArgumentParser()

parser.add_argument(
    '--config',
    type=str,
    help='Path to a Kafka or PubSub config file',
    default=""
)

args = parser.parse_args()

if __name__ == "__main__":

    sender = Sender()
    sender.setup(config_file="config/kafka/producer.json")
    pid = str(os.getpid())
    msg = json.dumps({"value": 100})
    sender.send(topic="test", key=pid, msg=msg, sync=True)