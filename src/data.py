import pytorch_lightning as pl
import torchvision
import torchvision.transforms as transforms
import torch

class FashionMNISTDataModule(pl.LightningDataModule):
    def __init__(self, batch_size, num_classes,  val_ratio, num_workers, transforms_args = {}, data_dir = "./data", ):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.val_ratio = val_ratio

        # Augmentation policy for training set
        train_transforms = [
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(degrees=10, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
            ]

        # Preprocessing steps applied to validation and test set.
        test_transforms = [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
            ]
        
        # Additional augmentations
        if transforms_args:
            if transforms_args["random_crop"]:
                train_transforms.insert(0, transforms.RandomCrop(28, padding=4))

            if transforms_args["random_erasing"]:
                train_transforms.append(
                    transforms.RandomErasing(
                        p=0.5,
                        scale=(0.02, 0.33),
                        ratio=(0.3, 3.3),
                        value="random",
                        inplace=False,
                        )
                )

        self.num_classes = num_classes
        self.augmentation = transforms.Compose(train_transforms)
        self.transform = transforms.Compose(test_transforms)

    def prepare_data(self):
        pass

    def setup(self, stage=None):

        # Torchvision has just a train/test split, adding val split
        train_val_dataset = torchvision.datasets.FashionMNIST(root=self.data_dir, download=True, transform=None)
        val_ratio = self.val_ratio
        nb_train = int((1.0 - val_ratio)*len(train_val_dataset))
        nb_val = len(train_val_dataset) - nb_train

        train_dataset, val_dataset = torch.utils.data.dataset.random_split(train_val_dataset, [nb_train, nb_val])
        test_dataset = torchvision.datasets.FashionMNIST(root=self.data_dir, download=True, train=False, transform=None)

        self.train, self.val, self.test = train_dataset, val_dataset, test_dataset
        self.train.dataset.transform = self.augmentation
        self.val.dataset.transform = self.transform
        self.test.transform = self.transform
        
    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers)

    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val, batch_size=self.batch_size, num_workers=self.num_workers)

    def test_dataloader(self):
        return torch.utils.data.DataLoader(self.test, batch_size=self.batch_size, num_workers=self.num_workers)