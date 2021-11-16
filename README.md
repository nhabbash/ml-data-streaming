# ML Data Streaming System

## Overview
This repository implements a system in which an app can query a ML service for inference requests. The app produces inference requests as messages in a topic of a message broker, the ML service can pull from it, run the inference and send back the result to the broker in another output topic. The app can then read and store the result from the output topic.

The system is composed of four components:
* [`/app`](app) - Application, using a unified API to communicate with either Google PubSub or Apache Kafka. It also contains instructions on how to launch PubSub and Kafka locally.
* [`/model_server`](model_server) - ML service model server, which deploys a trained model with microservices using Seldon Core.
* [`/training`](training) - Training utilities, containing the code defining the model, the dataset, training script and experiment tracking.
* [`/resources`](resources) - Deployment resources, containing configuration files to orchestrate the components as pods in Kubernetes.

Each component has instructions on how to test it individually.
## Installation
```sh
$ git clone https://github.com/nhabbash/ml-data-streaming
$ cd ml-data-streaming
```

## Notes
The system works in stages (app to broker communication, model server querying) but still isn't set up to work completely.
