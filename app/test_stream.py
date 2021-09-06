import argparse
import uuid
import json
from src.utils import NumpyArrayEncoder, load_mnist, preprocess_images, get_batch
from src.Sender import Sender, send_cb
from src.Receiver import Receiver, receive_cb
from src.Message import Message

parser = argparse.ArgumentParser()

parser.add_argument(
    '--To',
    type=str,
    help='Default message broker to send to',
    default='kafka',
    choices=('kafka', 'pubsub'))

parser.add_argument(
    '--From',
    type=str,
    default='kafka',
    help='Default message broker to receive from',
    choices=('kafka', 'pubsub'))

parser.add_argument(
    '--sender_conf',
    type=str,
    help='Path to a producing config file',
    default='config/kafka/sender.json')

parser.add_argument(
    '--kafka_admin_conf',
    type=str,
    help='Path to a Kafka admin config file, needed if sending to Kafka',
    default='config/kafka/admin.json'
)

parser.add_argument(
    '--receiver_conf',
    type=str,
    help='Path to a receiving config file',
    default='config/kafka/receiver.json')

parser.add_argument(
    '--topic_conf',
    type=str,
    help='Path to the topic configuration', 
    default='config/topics.json')

args = parser.parse_args()

if __name__ == '__main__':

    with open(args.sender_conf, 'r') as file:
        sender_conf = json.load(file)
    
    with open(args.receiver_conf, "r") as file:
        receiver_conf = json.load(file)

    with open(args.topic_conf, 'r') as file:
        topic_conf = json.load(file)

    sender = Sender(conf=sender_conf, to=args.To)

    if args.To != args.From:
        raise Exception("Message broker FROM and TO have to be the same")

    if args.To == 'kafka':
        with open(args.kafka_admin_conf, 'r') as file:
            admin_conf = json.load(file)
        sender._sender._init_admin_config(conf=admin_conf) # Needed to create topics for Kafka

    for _, val in topic_conf.items():
        sender.create_topic(val)

    topic_in = topic_conf['topic_in']

    ####### Consuming data
    receiver = Receiver(conf=receiver_conf, _from=args.From)
    topic_out = topic_conf["topic_in"]
    print(f"#### Receiver: Subscribing to topic {topic_out}")
    receiver.subscribe(topic_out)

    print(f"#### Receiver: Listening for messages in topic {topic_out}...\n")
    receiver.receive(timeout=0, callback=receive_cb)

    ####### Producing data
    x, y = load_mnist('data/')
    x = preprocess_images(x)

    batch_size = 1
    x_batches = get_batch(x, batch_size)
    print('#### Producer: Sending messages...')
    for i in range(10):
        key = uuid.uuid4().hex[:4]
        payload = {'ndarray': x_batches[i]}
        encoded_payload = json.dumps(payload, cls=NumpyArrayEncoder)
        msg = Message(key=key, value=encoded_payload)
        sender.send(topic=topic_in, msg=msg, callback=send_cb)

    sender.flush()
    receiver.close()
    print("Finish")



