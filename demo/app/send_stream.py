import argparse
import uuid
import json
import time
from random import randrange
from src.utils import NumpyArrayEncoder, load_mnist, preprocess_images, get_batch
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

    # Reading data
    x, y = load_mnist("data/")
    x = preprocess_images(x)

    batch_size = 8
    x_batches = get_batch(x, batch_size)
    print("Sending...")
    for i in range(100):
        key = uuid.uuid4().hex[:4] # Assigning unique key to each message
        #print(x_batches[i].nbytes/1e6) batch size
        payload = {"ndarray": x_batches[i]}
        encoded_payload = json.dumps(payload, cls=NumpyArrayEncoder)
        msg = Message(key=key, value=encoded_payload)
        sender.send(topic=topic_in, msg=msg, callback=delivery_ack)
        time.sleep(0.1)
    sender.flush()