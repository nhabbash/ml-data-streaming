# Fashion Recognizer - ML Service
This ML service deploys a model trained on Fashion MNIST. It can be deployed on K8s 


## Local testing

Launch the service locally:
```sh
$ pip install -r requirements.txt
$ seldon-core-microservice FashionClassifier --service-type MODEL
```

Build an image and launch a container:
```sh
$ docker build -t fashion-classifier .
$ docker run --name fashion-classifier -d --rm -p 9001:9000 fashion-classifier
```

Launch it as a pod in a cluster on K8s:
```sh
$ kind create cluster --name local

# Installing Istio as ingress for the cluster
$ istioctl install --set profile=demo -y
$ kubectl label namespace default istio-injection=enabled
$ kubectl create -f resources/seldon-gateway.yaml -n istio-system

# Installing Seldon Core and deploying model
$ kubectl create namespace seldon-system
$ helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --namespace seldon-system \
    --set istio.enabled=true
$ kubectl rollout status deploy/seldon-controller-manager -n seldon-system

# Deploy ML Service
$ kubectl apply -f resources/ml-service.yaml

# Port forward Istio Gateway to access ML Service
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080
```

Sending request:
```sh
# Locally or to Docker
$ curl http://localhost:9001/api/v1.0/predictions -H 'Content-Type: application/json' -d @test_input.json # Use the correct port
```
For K8s deployments the requests can be sent from the Swagger UI accessible from : `http://<ingress_url>/seldon/<namespace>/<model-name>/api/v1.0/doc/` (which should map to `localhost:8004/seldon/default/fashion-classifier/api/v1.0/doc/`)