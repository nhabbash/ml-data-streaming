# Training - Fashion Clothes Recognizer
This folder collects utilities to train and test a CNN on a given dataset for an image classification task.

The code is based on Pytorch Lightning.

## Quickstart

### Loading dataset
```python
# Loading Fashion MNIST
BATCH_SIZE=64
NUM_CLASSES=10
dm = FashionDataModule(num_classes=NUM_CLASSES, batch_size=BATCH_SIZE, num_workers=4)
dm.setup()

# Loading custom dataset
BATCH_SIZE=64
NUM_CLASSES=6
SPLIT = [0.7, 0.15, 0.15] # Dataset split
CSV_FILE = "data/datasets/fashion-products-small/preprocessed_labels.csv"
DS_DIR = "data/datasets/fashion-products-small/images"

INFO = {
    "csv_file": CSV_FILE,
    "ds_dir": DS_DIR,
    "split": SPLIT
}
AUGMENT = {"random_crop": True, "random_erasing": True, "random_perspective": True, "random_affine": True}

dm = FashionDataModule(num_classes=NUM_CLASSES, transforms_args=AUGMENT, custom_ds_info=INFO)
dm.setup()

dataiter = iter(dm.train_dataloader())
images, labels = dataiter.next()
```

Note that to load a custom dataset you'll need to provide a `csv` file formatted as `image_id, label`, where `image_id` is the name of the image (without extension) and `label` is its class. Check out the class `src.data.FashionDataset` to see how the images are read. 

### Training and testing
```python
trainer = pl.Trainer(max_epochs=EPOCHS,
                    auto_lr_find=True,
                    logger=logger,
                    callbacks=callbacks)

trainer.tune(model, datamodule=dm)
trainer.fit(model, dm)
trainer.test(ckpt_path="best")
```
### Logging
Logging is provided by [Weights and Biases](https://wandb.ai/). You can check the current dashboard for this project [here](https://wandb.ai/dodicin/mlops-project).

### Utilities
* Jupyter Notebook for interactive testing under [`testing.ipynb`](testing.ipynb)
* Unit tests for the model and the dataloader under [`tests.py`](tests.py)
* CLI training script under [`train.py`](train.py) (use `python train.py -h` for the arguments)
* Training configurations under [`config/`](config) to be run with the command `python train.py --json config/test_run_config.json`. Note that using the configuration overrides the other arguments passed to the script. The configuration has to have the following fields:

```sh
  * gpu: bool           # Train on GPU or not
  * augment: bool       # Use data augmentation
  * pruning: bool       # Prune during training
  * num_classes: int    # Number of classes
  * batch_size: int     # Batch size
  * epochs: int         # Epochs
  * fine_tune: bool     # Fine tune or feature extract
  * run_dir: str        # Where to save run files
  * custom_ds: bool     # Whether to use a custom DS
  * csv_file: str       # Path to the CSV containing the labels
  * ds_dir: str         # Path to the image folder
  * split: list         # Split
  * num_runs: int       # How many runs to make
  * fast_dev_run: bool  # Runs 1 batch of train, val and test to find any bugs 
```

## Notes
The CNN is composed of a pretrained ResNet18 and an additional classification layer. It's possible to train the model as a feature extractor, by freezing the ResNet and training only the classification layer, or fine tuning the whole model.