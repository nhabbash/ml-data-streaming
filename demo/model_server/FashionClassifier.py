import onnxruntime as onnxrt
import numpy as np
import os

class FashionClassifier:
    def __init__(self):
        self.loaded = False
        self.classes = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
        self.model = None

    def load(self):
        print(f"Loading model @{os.getpid()}")
        self.model = onnxrt.InferenceSession("model.onnx")
        print("Loaded model")

    def predict(self, x, names=None, meta=None):
        x = self.transform_input(x)
        onnx_inputs = {self.model.get_inputs()[0].name: x}
        logits = self.model.run(None, onnx_inputs)[0]
        preds = np.argmax(logits, axis=1)
        preds = self.transform_output(preds)
        return preds

    def transform_input(self, x, names=None, meta=None):
        mean = 255 * 0.1307
        stdDev = 255 * 0.3081
        x = (x - mean) / stdDev
        return x.astype("float32")

    def transform_output(self, y, names=None, meta=None):
        return y

    def health_status(self):
        response = self.predict(np.random.rand(*[2, 1, 28, 28]))
        assert len(response) > 0, "Health Check failed, no response"
        return response