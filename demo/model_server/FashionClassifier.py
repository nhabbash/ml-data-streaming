from models import ResNet18
import torchvision.transforms as transforms
import numpy as np
import os

class FashionClassifier:
    def __init__(self):
        self.loaded = False
        self.transforms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
            ])
        self.classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

    def load(self):
        print("Loading model",os.getpid())
        model_path = "model.ckpt"
        self._model = ResNet18.load_from_checkpoint(model_path)
        self.loaded = True
        print("Loaded model")

    def predict_orig(self, X, names=None, meta=None):
        X = self.transform_input(X)
        _, preds = self._model.predict(X)
        preds = self.transform_output(preds)
        return [preds]
    
    def predict(self, X, names=None):
        return [X[0]+" - processed"]

    def transform_input(self, X, names=None, meta=None):
        X = self.transforms(X)
        X = X.unsqueeze(0)
        X = X.float()
        return X

    def transform_output(self, X, names=None, meta=None):
        X = X.numpy()[0]
        return self.classes[X]

    def health_status(self):
        response = self.predict_orig(np.random.rand(*[28, 28, 1]))
        assert len(response) == 1, "Health Check failed, multiple predictions"
        assert isinstance(response[0], str), "Health Check failed, class label not a str"
        return response
