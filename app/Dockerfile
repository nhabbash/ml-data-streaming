FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# To connect to the PubSub Emulator
ENV PUBSUB_EMULATOR_HOST=localhost:8085 
ENV PUBSUB_PROJECT_ID=tokyo-rain-123

CMD [ "python3", "app.py"]