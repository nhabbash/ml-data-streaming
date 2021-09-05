FROM python:3.7-slim
COPY . /model_server
WORKDIR /model_server
RUN pip install -r requirements.txt
# Port for GRPC
EXPOSE 5000
# Port for REST
EXPOSE 9000

# Define environment variable
ENV MODEL_NAME FashionClassifier
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE=0

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE