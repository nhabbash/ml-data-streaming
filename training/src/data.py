from logging import root
import torch
import torchvision
import torchvision.transforms as transforms
import pytorch_lightning as pl
from sklearn.model_selection import train_test_split
from PIL import Image

import numpy as np
import pandas as pd

from .utils import LabelEncoder

class FashionDataModule(pl.LightningDataModule):
    """DataModule class, sets up the dataset and creates dataloader

        Attributes:
            batch_size (int): Batch size
            num_workers (int): Threads per dataloader
            custom_ds_info (dict): Dictionary containing data on the custom dataset to be used. If None it defaults to Fashion MNIST.
                                    The dictionary must be formatted as:
                                    {
                                        "csv_file": path_to_csv_file,
                                        "ds_dir": path_to_images_dir
                                        "split": list_of_splits such as [0.7, 0.15, 0.15]
                                    }
            num_classes (int): Number of classes
    """     
    def __init__(self, num_classes, transforms_args = {}, custom_ds_info = None, batch_size=128, num_workers=4):
        super().__init__()

        self.batch_size = batch_size
        self.num_workers = num_workers

        if custom_ds_info:
            assert list(custom_ds_info.keys()) == ["csv_file", "ds_dir", "split"]
            assert isinstance(custom_ds_info["split"], list) and len(custom_ds_info["split"]) == 3 and sum(custom_ds_info["split"]) == 1
            
            self.custom_ds_info = custom_ds_info
            self.use_MNIST = False
            self.num_classes = num_classes
        else:
            self.dataset_path = "data/datasets"
            self.use_MNIST = True
            self.num_classes = 10
            self.val_split = 0.15

        # Augmentation policy for training set
        train_transforms = [
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize(size=(28, 28)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.445,), (0.269,)) # Mean and STD of ImageNet greyscaled
            ]

        # Preprocessing steps applied to validation and test set.
        test_transforms = [
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize(size=(28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.445,), (0.269,)), # Mean and STD of ImageNet greyscaled
            ]
        
        # Additional augmentations
        if transforms_args:
            if transforms_args["random_affine"]:
                train_transforms.append(transforms.RandomAffine(degrees=15, translate=(0.1, 0.1)))
            
            if transforms_args["random_crop"]:
                train_transforms.append(transforms.RandomResizedCrop(size=24, scale=(0.5, 1.0), ratio=(0.8, 1.3)))

            if transforms_args["random_erasing"]:
                train_transforms.append(
                    transforms.RandomErasing(
                        p=0.3,
                        scale=(0.01, 0.2),
                        ratio=(0.3, 3.3),
                        value=0,
                        inplace=False,
                        )
                )
            if transforms_args["random_perspective"]:
                train_transforms.append(
                    transforms.RandomPerspective(distortion_scale=0.3, p=0.3)
                )

        self.augmentation = transforms.Compose(train_transforms)
        self.transform = transforms.Compose(test_transforms)

    def prepare_data(self):
        pass

    def setup(self, stage=None):
        if self.use_MNIST:
            self.setup_MNIST()
        else:
            self.setup_custom_ds()
    
    def setup_custom_ds(self):
        """Creates custom dataset, split in train/val/test according to the passed split
        """        
        csv_file = self.custom_ds_info["csv_file"]
        ds_dir = self.custom_ds_info["ds_dir"]
        split_train, val_split, test_split = self.custom_ds_info["split"]

        train_dataset = FashionDataset(ds_dir=ds_dir, csv_file=csv_file, transform=self.augmentation)
        val_dataset = FashionDataset(ds_dir=ds_dir, csv_file=csv_file, transform=self.transform)
        test_dataset = FashionDataset(ds_dir=ds_dir, csv_file=csv_file, transform=self.transform)

        # Create the index splits for training, validation and test
        y_full = train_dataset.label_encoder.encode(train_dataset.df.label.values)

        train_idx, remainder = train_test_split(np.arange(len(y_full)), test_size=1-split_train, shuffle=True, stratify=y_full)

        y_remainder = train_dataset.label_encoder.encode(train_dataset.df.iloc[remainder.tolist()].label.values)

        new_split_val = 1/((1 - split_train)/val_split)
        val_idx, test_idx = train_test_split(np.arange(len(y_remainder)), test_size=new_split_val, shuffle=True, stratify=y_remainder)

        train_dataset = torch.utils.data.Subset(train_dataset, train_idx)
        val_dataset = torch.utils.data.Subset(val_dataset, val_idx)
        test_dataset = torch.utils.data.Subset(test_dataset, test_idx)

        self.train, self.val, self.test = train_dataset, val_dataset, test_dataset
        
    def setup_MNIST(self):
        """Creates Fashion MNIST dataset, split into train/val/test
        """        
        # Torchvision has just a train/test split, adding val split
        train_dataset = torchvision.datasets.FashionMNIST(root="/tmp", download=True, transform=self.augmentation)
        val_dataset = torchvision.datasets.FashionMNIST(root="/tmp", download=True, transform=self.transform)

        # Create the index splits for training, validation and test
        y_train = train_dataset.targets

        train_idx, val_idx = train_test_split(
            np.arange(len(y_train)), test_size=self.val_split, shuffle=True, stratify=y_train)

        # Define samplers for obtaining training and validation batches
        train_dataset = torch.utils.data.Subset(train_dataset, train_idx)
        val_dataset = torch.utils.data.Subset(val_dataset, val_idx)
        test_dataset = torchvision.datasets.FashionMNIST(root="/tmp", download=True, train=False, transform=self.transform)

        self.train, self.val, self.test = train_dataset, val_dataset, test_dataset

    def train_dataloader(self, batch_size=128, num_workers=4):
        return torch.utils.data.DataLoader(self.train,
                    shuffle=True, 
                    batch_size=self.batch_size if self.batch_size is not None else batch_size, 
                    num_workers=self.num_workers if self.num_workers is not None else num_workers)


    def val_dataloader(self, batch_size=128, num_workers=4):
        return torch.utils.data.DataLoader(self.val, 
                    batch_size=self.batch_size if self.batch_size is not None else batch_size, 
                    num_workers=self.num_workers if self.num_workers is not None else num_workers)

    def test_dataloader(self, batch_size=128, num_workers=4):
        return torch.utils.data.DataLoader(self.test,
                    batch_size=self.batch_size if self.batch_size is not None else batch_size, 
                    num_workers=self.num_workers if self.num_workers is not None else num_workers)

class FashionDataset(torch.utils.data.Dataset):
    """Custom Fashion Items dataset."""

    def __init__(self, csv_file, ds_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            ds_dir (string): Directory containing the images.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.df = pd.read_csv(csv_file, on_bad_lines="skip")

        # Process CSV
        self.df = self.df.astype("string")
        self.ds_dir = ds_dir
        self.transform = transform
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.df.label.values)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        image_id, y = self.df.iloc[idx]
        
        y = self.label_encoder.encode([y])[0]
        path = self.ds_dir + "/" + image_id + ".jpg"
        image = Image.open(path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, y