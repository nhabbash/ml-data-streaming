Testing locally: 
```sh
$ seldon-core-microservice FashionClassifier --service-type MODEL
```

Testing container: 
```sh
$ docker build -t "fashionclassifier-test" .
$ docker run --name "fashionclassifier-test" -d --rm -p 9001:9000 fashionclassifier
```

Sending request:
```sh
$ curl http://localhost:9001/api/v1.0/predictions -H 'Content-Type: application/json' -d '{"data": {"names": ["input"], "ndarray": ["TEST"]}}' # For the test build
$ curl localhost:9001/health/status # Actually tests the deployed model
```