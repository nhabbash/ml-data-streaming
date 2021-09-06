# ML Service - Fashion Recognizer
This ML service deploys a model trained on Fashion MNIST. It uses Seldon Core to convert the model into production microservices.

The service can be deployed locally, on Docker or on K8s.

# Usage
The wrapper `FashionClassifier` wraps over the model which will be then exposed by Seldon Core, served with Gunicorn. To implement different different endpoints follow [here](https://docs.seldon.io/projects/seldon-core/en/latest/python/python_component.html). The endpoints implemented in this version are:
* `api/v1.0/predictions`, which takes in a payload of the form `{"data": {"ndarray": [np.random.rand(*[batch_size, 1, H, W])]}}`
* `health/status`, returns whether `predictions` is working

The model has been exported by the trained models in [`../training`](../training) as an ONXX model, and is being instantiated as an ONXXRuntime.

# Deployment

## Launch the service locally:
### Prerequisites
* Python
```sh
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ seldon-core-microservice FashionClassifier --service-type MODEL
```

## Build an image and launch a container with Docker:
### Prerequisites
* Docker
```sh
$ docker build -t nhabbash/fashion-classifier .
$ docker run --name fashion-classifier -d --rm -p 9001:9000 nhabbash/fashion-classifier
```

## Deploy in a pod on K8s
The configuration for deploying on K8s is under `..\resources\ml-services.yaml`. It uses Native Kafka Stream Processing to create request streams for the input prediction.
### Prerequisites
* A K8s environment (Kind/Minikube)
* Istio (Ingress)
* Helm

```sh
$ kind create cluster --name local

# Installing Istio as ingress for the cluster
$ istioctl install --set profile=demo -y
$ kubectl label namespace default istio-injection=enabled
$ kubectl create -f ../resources/seldon-gateway.yaml -n istio-system

# Installing Seldon Core and deploying model
$ kubectl create namespace seldon-system
$ helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --namespace seldon-system \
    --set istio.enabled=true
$ kubectl rollout status deploy/seldon-controller-manager -n seldon-system

# Deploy ML Service
$ kubectl apply -f ../resources/ml-service.yaml
# Wait for it to be ready
$ kubectl wait --for=condition=available --timeout=600s deployment.apps/fashion-classifier-default-0-classifier

# Port forward Istio Gateway to access ML Service
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080
```

## Sending request:
```sh
# Send requests locally or to container
$ curl http://localhost:9001/api/v1.0/predictions -H 'Content-Type: application/json' -d @test_input.json
```

For K8s deployments the requests can be sent from the Swagger UI accessible from:
* `http://<ingress_url>/seldon/<namespace>/<model-name>/api/v1.0/doc/` (which should map to [`localhost:8004/seldon/default/fashion-classifier/api/v1.0/doc/`](localhost:8004/seldon/default/fashion-classifier/api/v1.0/doc/))

You can copy the payloads from the provided examples [`test_input_single.json`](test_input_single.json) or [`test_input.json`](test_input.json).