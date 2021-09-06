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
The library is comprised of 3 components:
* `Sender(conf, to)` class, responsible for sending messages to the configured message broker
    * `create_topic(topic)`: creates a topic from a topic name
    * `send(topic, msg, callback=send_cb)`: sends a `Message` msg to the configurated broker
* `Receiver(conf, from)` class, responsible for receiving messages to the configured message broker
    * `subscribe(topic)`: subscribes to a topic from a topic name if it exists
    * `receive(timeout=None, callback=receive_cb):`: listens to messages from the subscription to the broker asynchronously. The messages are processed in the callback passed to it.
* `Message` class, responsible for transforming the messages to a unified format.

The callbacks passed to the `receive` and `send` methods have to be decorated with the decorators provided in the `decorators` module, `@on_delivery` and `@on_receive`, which format the incoming payload to a `Message` object.

The configuration for each message broker is kept under `config/`.

An `Application` example class is provided, which wraps over a `Sender` and `Receiver` and simulates broker interactions and broker changes during runtime, such as communicating with Kafka first and then PubSub from the same context.

## Utilities
* Example application: `app.py`, need to have a PubSub Emulator and Kafka instances open, simulates connecting to one and then the other and reading/writing to them.
* Test read/write: `test_stream.py`, tests reading and writing to a message broker, support arguments for options (`see python test_stream.py -h`)

The scripts send as payloads encoded numpy arrays from the Fashion MNIST test dataset, located under `./data/`. 

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

# Kafka
$ python test_stream.py # Arguments default to Kafka

# PubSub
$ python test_stream.py --To pubsub --From pubsub --receiver_conf config/pubsub/receiver.json --sender_conf config/pubsub/sender.json

# Example application
$ python app.py

# Run app inside a container (PubSub might not work)
$ docker build -t nhabbash/stream-app .
$ docker run --rm --network host --name stream-app nhabbash/stream-app

# Run app inside pod in K8s (Won't connect to anything)
$ kubectl apply -f ../resources/stream-app-config.yml
# Check that it's running
$ kubectl logs stream-app-<id>
```