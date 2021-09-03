import argparse
import uuid
import json
import time
from random import randrange
from src.Sender import Sender, delivery_ack
from src.Message import Message

parser = argparse.ArgumentParser()

parser.add_argument(
    '--To',
    type=str,
    help='Default message broker to send to',
    choices=('kafka', 'pubsub'), required=True)

parser.add_argument(
    '--sender_conf',
    type=str,
    help='Path to a producing config file', 
    required=True)

parser.add_argument(
    '--kafka_admin_conf',
    type=str,
    help='Path to a Kafka admin config file, needed if sending to Kafka',
    default="config/kafka/admin.json"
)

parser.add_argument(
    '--topic_conf',
    type=str,
    help='Path to the topic configuration', 
    default='config/topics.json')

args = parser.parse_args()

if __name__ == "__main__":

    with open(args.sender_conf, "r") as file:
        sender_conf = json.load(file)

    with open(args.topic_conf, "r") as file:
        topic_conf = json.load(file)

    conf_to = args.sender_conf.split("/")[1]
    if conf_to != args.To:
        raise Exception(f"Configuration mismatch: trying to send to {args.To} with configuration for {conf_to}")
        
    sender = Sender(conf=sender_conf, to=args.To)

    if args.To == "kafka":
        sender._sender._init_admin_config(config_file=args.kafka_admin_conf) # Needed to create topics for Kafka

    for _, val in topic_conf.items():
        sender.create_topic(val)

    sender.list_topics()

    topic_in = topic_conf["topic_in"]
    key = uuid.uuid4().hex[:4]

    print("Sending")
    while True:
        val = json.dumps({"value": randrange(100)})
        msg = Message(key=key, value=val)
        sender.send(topic=topic_in, msg=msg, callback=delivery_ack)
        sender.flush()
        time.sleep(0.1)
    