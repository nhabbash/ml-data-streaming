# Unified API for Google PubSub and Kafka
This library presents a unified API for sending and receiving messages from Google PubSub or Apache Kafka asynchronously. The library has a single interface to communicate with both, presenting the same methods of access, and transforms the messages from both message brokers to the same format.

## Quickstart
```python
from src.Sender import Sender
from src.Receiver import Receiver
from src.Message import Message
from src.decorators import on_receive, on_delivery

# Sending
sender = Sender(conf=sender_conf, to=mb) # mb in ["kafka", "pubsub"]
if args.To == 'kafka':
    sender._sender._init_admin_config(config_file=kafka_admin_conf)

topic = "topic"
sender.create_topic(topic)
key = "abcd"
msg = Message(key=key, value={"Hello": "World")

# Callback called on delivery
@on_delivery
def send_cb(err, msg_id):
    if not err: print("Sent msg")

sender.send(topic=topic, msg=msg, callback=send_cb)
sender.flush()

# Receiving
receiver = Receiver(conf=receiver_conf, _from=mb)
topic = "topic"
receiver.subscribe(topic)

# Callback called on receiving, process messages here!
@on_receive
def receive_cb(err, msg):
    if not err: print(f"Received msg: {msg}")

receiver.receive(callback=receive_cb)
receiver.close()
```

## Usage
The library is comprised of three components:
* `Sender(conf, to)` class, responsible for sending messages to the configured message broker
    * `create_topic(topic)`: creates a topic from a topic name
    * `send(topic, msg, callback=send_cb)`: sends a `Message` msg to the configurated broker
* `Receiver(conf, from)` class, responsible for receiving messages to the configured message broker
    * `subscribe(topic)`: subscribes to a topic from a topic name if it exists
    * `receive(timeout=None, callback=receive_cb):`: listens to messages from the subscription to the broker. The messages are processed in the callback passed to it.
* `Message` class, responsible for transforming the messages to a unified format.

The callbacks passed to the `receive` and `send` methods have to be decorated with the decorators provided in the `decorators` module, `@on_delivery` and `@on_receive`, which format the incoming payload to a `Message` object.

The configuration for each message broker is kept under `config/`.

## Application
* Sender process: `send_stream.py`
* Receiver process: `receive_stream.py`
* Application (does both): `app.py`

```sh
usage: app.py [-h] [--To {kafka,pubsub}] [--From {kafka,pubsub}] [--sender_conf SENDER_CONF]
              [--kafka_admin_conf KAFKA_ADMIN_CONF] [--receiver_conf RECEIVER_CONF] [--topic_conf TOPIC_CONF]

optional arguments:
  -h, --help            show this help message and exit
  --To {kafka,pubsub}   Default message broker to send to
  --From {kafka,pubsub}
                        Default message broker to receive from
  --sender_conf SENDER_CONF
                        Path to a producing config file
  --kafka_admin_conf KAFKA_ADMIN_CONF
                        Path to a Kafka admin config file, needed if sending to Kafka
  --receiver_conf RECEIVER_CONF
                        Path to a receiving config file
  --topic_conf TOPIC_CONF
                        Path to the topic configuration
```
The application sends as payloads encoded numpy arrays from the Fashion MNIST test dataset, located under `./data/`. 


## Starting Kafka locally
### Prerequisites:
* Docker/Docker Compose
```sh
$ docker-compose up #Starts a Kafka and a Zookeeper container
```

## Starting PubSub emulator locally

### Prerequisites
* Google Cloud SDK
* Google Cloud PubSub emulator

```sh
$ gcloud beta emulators pubsub start --project=tokyo-rain-123 --host-port=8085
$ gcloud init --console-only # login, no need to set up any projects

# Set these variables in the terminal you're running the application in
$ gcloud beta emulators pubsub env-init
$ export PUBSUB_EMULATOR_HOST=localhost:8085 
$ export PUBSUB_PROJECT_ID=tokyo-rain-123


$ unset PUBSUB_EMULATOR_HOST # When finished
```

## Commands
```sh
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt

# PubSub
$ python receive_stream.py --From pubsub --receiver_conf config/pubsub/subscriber.json
$ python send_stream.py --To pubsub --sender_conf config/pubsub/publisher.json

# Kafka
$ python receive_stream.py --From kafka --receiver_conf config/kafka/consumer.json
$ python send_stream.py --To kafka --sender_conf config/kafka/producer.json

# Defaults to Kafka for both sending and receiving, the app can work with PubSub but it won't receive any messages as the subscription is made after the Publisher sends messages
$ python app.py

# Run app inside a container
$ docker build -t fashion-app .
$ docker run --rm --network host --name fashion-app fashion-app
```