Testing locally: 
```sh
$ seldon-core-microservice FashionClassifier --service-type MODEL
```

Testing container: 
```sh
$ docker build -t fashion-classifier .
$ docker run --name fashion-classifier -d --rm -p 9001:9000 fashion-classifier
$ docker stop fashion-classifier
```

Sending request:
```sh
$ curl http://localhost:9001/api/v1.0/predictions -H 'Content-Type: application/json' -d @test_input.json # Use the correct port
$ curl localhost:9001/health/status
```