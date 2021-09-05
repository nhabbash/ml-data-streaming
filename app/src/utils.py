import os
import gzip
import numpy as np
from json import JSONEncoder

def load_mnist(path):
    """Load MNIST from path

    Args:
        path (str): Path where the archive is saved

    Returns:
        images (mp.ndarray), labels (np.ndarray): examples and labels 
    """    
    labels_path = os.path.join(path,
                            't10k-labels-idx1-ubyte.gz')
    images_path = os.path.join(path,
                            't10k-images-idx3-ubyte.gz')

    with gzip.open(labels_path, 'rb') as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                            offset=8)

    with gzip.open(images_path, 'rb') as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                            offset=16).reshape(len(labels), 784)

    return images, labels

def preprocess_images(x):
    """Preprocess images for usage by casting to float and reshaping them as CWH

    Args:
        x (np.ndarray): batch of images

    Returns:
        x (np.ndarray): reshaped batch of images
    """    
    x = x.astype('float32') / 255
    x = x.reshape(x.shape[0], 1, 28, 28)
    return x

def get_batch(x, batch_size):
    """Splits images in batches

    Args:
        x (np.ndarray): Images
        batch_size (int): Batch size

    Returns:
        batches (np.ndarray): Images splits in batches (with remaineder)
    """    
    return np.split(x, np.arange(batch_size, len(x), batch_size))

class NumpyArrayEncoder(JSONEncoder):
    """Numpy Encoder to JSON for serialization
    """    
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)