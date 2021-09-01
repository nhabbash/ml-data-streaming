import unittest

from models import *
from data import *
from utils import *

class DataTest(unittest.TestCase):
    def setUp(self):
        # loading data
        BATCH_SIZE=1
        NUM_CLASSES=10
        VAL_RATIO=.15
        NUM_WORKERS=1
        self.dm = FashionMNISTDataModule(batch_size=BATCH_SIZE, num_classes=NUM_CLASSES, val_ratio=VAL_RATIO, num_workers=NUM_WORKERS, data_dir="/tmp")
        self.dm.setup()

    def test_shape(self):
        sample, _ = self.dm.train[0]
        self.assertEqual(torch.Size((1, 28, 28)), sample.shape)

    def test_single_process_dataloader(self):
        with self.subTest(split='train'):
            self._check_dataloader(self.dm.train_dataloader(num_workers=0))
        with self.subTest(split='test'):
            self._check_dataloader(self.dm.test_dataloader(num_workers=0))

    def test_multi_process_dataloader(self):
        with self.subTest(split='train'):
            self._check_dataloader(self.dm.train_dataloader(num_workers=2))
        with self.subTest(split='test'):
            self._check_dataloader(self.dm.test_dataloader(num_workers=2))

    def _check_dataloader(self, loader):
        for _ in loader:
            pass

class TestResNet(unittest.TestCase):
    def setUp(self):
        NUM_CLASSES = 10
        INPUT_SHAPE = [1, 28, 28]
        FINE_TUNE = False

        self.model = ResNet18(INPUT_SHAPE, NUM_CLASSES, FINE_TUNE)
        self.dummy_input = torch.randn([4]+INPUT_SHAPE, dtype=torch.float)


if __name__ == "__main__":
    unittest.main()