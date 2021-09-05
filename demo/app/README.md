# Application - Unified API for Google PubSub and Kafka
This is an example application using a unified API for sending and receiving messages with Google PubSub or Apache Kafka as message brokers.

A short tutorial:
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
    if not err: print("Received msg")

receiver.receive(callback=receive_cb)
receiver.close()
```

The callbacks passed to the `receive` and `send` methods have to be decorated with the decorators provided in the `decorators` module to allow for marshalling the formats to a `Message` object, which is used to parse messages both from Kafka and Pubsub.

The configuration for each message broker is kept under `config/`, and can be expanded on necessity.

## Local testing
## Starting Kafka locally
### Prerequisites:
* Docker/Docker Compose
```sh
$ docker-compose up & #Starts a Kafka and a Zookeeper container
```

## Starting PubSub emulator locally

### Prerequisites
* Google Cloud SDK
* Google Cloud PubSub emulator

```sh
gcloud init --console-only # login, no need to set up any projects

export PUBSUB_EMULATOR_HOST=localhost:8085
export PUBSUB_PROJECT_ID=tokyo-rain-123

gcloud beta emulators pubsub start --project=tokyo-rain-123 --host-port 8085

unset PUBSUB_EMULATOR_HOST # When finished
```

## Commands
```sh
# PubSub
$ python send_stream.py --To pubsub --sender_conf config/pubsub/publisher.json
$ python receive_stream.py --From pubsub --receiver_conf config/pubsub/subscriber.json

# Kafka
$ python send_stream.py --To kafka --sender_conf config/kafka/producer.json
$ python receive_stream.py --From kafka --receiver_conf config/kafka/consumer.json

# Defaults to Kafka for both sending and receiving
$ python app.py

# Run app inside a container
$ docker build -t fashion-app .
$ docker run --rm --network host --name fashion-app fashion-app
```