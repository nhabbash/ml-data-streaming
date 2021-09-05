# System Architecture

(Pic)

## Prerequisites
* Kind
* Helm
* Istio

## Installation
```sh
$ kind create cluster --name local
$ kubectl create clusterrolebinding default-admin --clusterrole cluster-admin --serviceaccount=default:default # Provide admin access to cluster
$ token=$(kubectl get secrets -o jsonpath="{.items[?(@.metadata.annotations['kubernetes\.io/service-account\.name']=='default')].data.token}"|base64 --decode) # Save token for use

# Install istio on the cluster
$ istioctl install --set profile=demo -y
$ kubectl label namespace default istio-injection=enabled
$ kubectl create -f resources/seldon-gateway.yaml -n istio-system
$ kubectl port-forward $(kubectl get pods -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].metadata.name}') -n istio-system 8004:8080 # Needed to access

# Get Seldon Core on the cluster
$ kubectl create namespace seldon-system
$ helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --namespace seldon-system \
    --set istio.enabled=true
$ kubectl rollout status deploy/seldon-controller-manager -n seldon-system

# Get and deploy Strimzi Kafka on the cluster
$ helm repo add strimzi https://strimzi.io/charts/
$ helm install fashion-mb strimzi/strimzi-kafka-operator
$ kubectl apply -f resources/kafka-config.yaml
$ kubectl apply -f resources/topics.yaml

# Deploy ML Service
$ kubectl apply -f resources/ml-service.yaml

```

```sh
# Dashboard
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.1.0/aio/deploy/recommended.yaml # Install dashboard
$ echo $token
# Visit http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```