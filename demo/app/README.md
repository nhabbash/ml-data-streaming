
# Starting Kafka locally
TODO: put local dockerfile

## Prerequisites

# Starting PubSub emulator locally

## Prerequisites
* Google Cloud SDK
* Google Cloud PubSub emulator

```sh
gcloud init --console-only # login, no need to set up projects

export PUBSUB_EMULATOR_HOST=localhost:8085
export PUBSUB_PROJECT_ID=tokyo-rain-123

gcloud beta emulators pubsub start --project=tokyo-rain-123 --host-port 8085

unset PUBSUB_EMULATOR_HOST # When finished
```

# Commands
```sh
# PubSub
$ python send_stream.py --To pubsub --sender_conf config/pubsub/publisher.json
$ python receive_stream.py --From pubsub --receiver_conf config/pubsub/subscriber.json

# Kafka
$ python send_stream.py --To kafka --sender_conf config/kafka/producer.json
$ python receive_stream.py --From kafka --receiver_conf config/kafka/consumer.json
```