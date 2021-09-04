import os
import gzip
import numpy as np
from json import JSONEncoder

def load_mnist(path, kind='t10k'):

    """Load MNIST data from `path`"""
    labels_path = os.path.join(path,
                            '%s-labels-idx1-ubyte.gz'
                            % kind)
    images_path = os.path.join(path,
                            '%s-images-idx3-ubyte.gz'
                            % kind)

    with gzip.open(labels_path, 'rb') as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                            offset=8)

    with gzip.open(images_path, 'rb') as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                            offset=16).reshape(len(labels), 784)

    return images, labels

def load_images(path):
    pass

def preprocess_images(x):
    x = x.astype('float32') / 255
    x = x.reshape(x.shape[0], 1, 28, 28)
    return x

def get_batch(x, batch_size):
    return np.split(x, np.arange(batch_size, len(x), batch_size))

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)