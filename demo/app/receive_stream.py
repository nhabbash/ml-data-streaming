import argparse
import os, sys, json
from src.Receiver import Receiver, process_res

parser = argparse.ArgumentParser()
parser.add_argument(
    '--From',
    type=str,
    help='Default message broker to receive from',
    choices=('kafka', 'pubsub'), required=True)

parser.add_argument(
    '--receiver_conf',
    type=str,
    help='Path to a receiving config file', 
    required=True)

parser.add_argument(
    '--topics_conf',
    type=str,
    help='Path to the topic configuration', 
    default='config/topics.json')

args = parser.parse_args()

if __name__ == "__main__":

    with open(args.receiver_conf, "r") as file:
        sender_conf = json.load(file)

    with open(args.topics_conf, "r") as file:
        topics_conf = json.load(file)

    conf_from = args.receiver_conf.split("/")[1]
    if conf_from != args.From:
        raise Exception(f"Configuration mismatch: trying to receive from {args.From} with configuration for {conf_from}")
        
    receiver = Receiver(conf=sender_conf, _from=args.From)
    topic = topics_conf["topic_in"]

    print(f"Subscribing to topic {topic}")
    receiver.subscribe(topic)

    print(f"Listening for messages...\n")
    receiver.receive(callback=process_res)
    receiver.close()