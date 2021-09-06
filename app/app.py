import uuid
import json
from src.utils import NumpyArrayEncoder, load_mnist, preprocess_images, get_batch
from src.Sender import send_cb
from src.Receiver import receive_cb
from src.Message import Message
from src.Application import Application

def communicate_with(broker):

    # Setup application
    app = Application()
    app.setup(broker=broker, config_path=f"config/{broker}")

    # Creating topics
    with open("config/topics.json", 'r') as file:
        topic_conf = json.load(file)

    for _, val in topic_conf.items():
        app.sender.create_topic(val)

    # Consuming data
    topic_write = topic_conf["topic_in"]
    print(f"#### APP: Subscribing to topic {topic_write}@{app.broker}")
    app.receiver.subscribe(topic_write)

    print(f"#### APP: Listening for messages in topic {topic_write}@{app.broker}...\n")
    # This receives on another thread
    app.receiver.receive(timeout=2, callback=receive_cb)

    # Producing data
    x, y = load_mnist('data/')
    x = preprocess_images(x)

    batch_size = 1
    x_batches = get_batch(x, batch_size)
    topic_read = topic_write
    print(f'#### APP: Sending messages to topic {topic_read}@{app.broker}')
    for i in range(10):
        key = uuid.uuid4().hex[:4]
        payload = {'ndarray': x_batches[i]}
        encoded_payload = json.dumps(payload, cls=NumpyArrayEncoder)
        msg = Message(key=key, value=encoded_payload)
        app.sender.send(topic=topic_read, msg=msg, callback=send_cb)

    app.sender.flush()
    app.receiver.close()

if __name__ == '__main__':
    print("\n\n\n############ KAFKA CONNECTION ############")
    try:
        communicate_with("kafka")
    except Exception as e:
        print(e)
    print("\n\n\n############ PUBSUB CONNECTION ############")
    try:
        communicate_with("pubsub")
    except Exception as e:
        # GCloud might require credentials inside Docker
        print(e)
    print("\n\n\n Finished")