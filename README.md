# MLOps Project

## Overview
This repository implements a system in which an app can produce inference requests to a topic of a message broker, a model server can pull from it, complete the request and send it back to the broker in another topic. The app can then read and store the completed inference from the output topic.

The system is composed of four components:
* [`/app`](app) - Application, using a unified API to communicate with either Google PubSub or Apache Kafka. It also contains instructions on how to launch PubSub and Kafka locally.
* [`/model_server`](model_server) - Model server, which deploys a trained model to microservices using Seldon Core.
* [`/training`](training) - Training utilities, containing the code defining the model, the dataset, and training script.
* [`/resources`](resources) - Deployment resources, containing configuration files to orchestrate the components as pods in Kubernetes.

Each component has instructions on how to test it individually.
## Installation
```sh
$ git clone https://github.com/nhabbash/mlops-project
$ cd mlops-project
```

