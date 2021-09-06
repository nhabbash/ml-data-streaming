import unittest

from src.models import ResNet18
from src.data import FashionDataModule
from src.utils import *

class DataTest(unittest.TestCase):
    def setUp(self):
        # loading data
        BATCH_SIZE=1
        NUM_CLASSES=10
        NUM_WORKERS=1
        self.dm = FashionDataModule(num_classes=NUM_CLASSES, batch_size=BATCH_SIZE, num_workers=NUM_WORKERS)
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
        self.num_classes = 10
        self.batch_size = 4
        self.input_shape = [1, 28, 28]

        self.model = ResNet18(num_classes=self.num_classes, fine_tune=False)
        self.dummy_input = torch.randn([self.batch_size]+self.input_shape, dtype=torch.float)

    @torch.no_grad()
    def test_shape(self):
        outputs = self.model(self.dummy_input)
        self.assertEqual(torch.Size((self.batch_size, self.num_classes)), outputs.shape)

    def test_all_parameters_updated(self):
        # Check if the model presents any dead sub-graph (unused components)

        optim = torch.optim.SGD(self.model.parameters(), lr=0.1)

        outputs = self.model(self.dummy_input)
        loss = outputs.mean()
        loss.backward()
        optim.step()

        for param_name, param in self.model.named_parameters():
            if param.requires_grad:
                with self.subTest(name=param_name):
                    self.assertIsNotNone(param.grad)
                    self.assertNotEqual(0., torch.sum(param.grad ** 2))

if __name__ == "__main__":
    unittest.main()