import argparse
import os
import json
import wandb

from src.models import *
from src.data import *
from src.utils import *

from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelPruning
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning import seed_everything

from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_recall_curve

import warnings
warnings.filterwarnings("ignore") # A lot of deprecated warnings in the last version of PyTorch

parser = argparse.ArgumentParser()

parser.add_argument(
    '--json',
    type=str,
    help='Path to a configuration JSON file, will override the other options',
    default=""
)

parser.add_argument(
    '--run_dir',
    type=str,
    help='Where to store the run files',
    default="./data/training_run/"
)

parser.add_argument(
    '--fine_tune',
    help='Fine tune the model instead of training just the last layer',
    type=bool,
    default=False
)

parser.add_argument(
    '--augment',
    help='Specify if you want to add data augmentation',
    type=bool,
    default=False
)

parser.add_argument(
    '--pruning',
    help='Specify if you want to prune the model',
    type=bool,
    default=False
)

parser.add_argument(
    '--use_gpu',
    help='Whether to use GPU',
    type=bool,
    default=True
)

parser.add_argument(
    '--batch_size',
    help='Specify the batch size to use during training',
    type=int,
    default=128
)

parser.add_argument(
    '--epochs',
    help='Specify the epochs to train for',
    type=int,
    default=50
)

parser.add_argument(
    '--num_runs',
    help='Specify the number of runs to execute',
    type=int,
    default=10
)

parser.add_argument(
    '--fast_dev_run',
    help='Test whether everything works',
    type=bool,
    default=False
)

args = parser.parse_args()

if args.json != "":
    with open(args.json, "r") as file:
        conf = json.load(file)

    print(f"Using configuration from {args.json}, ignoring other arguments...")

    # Some hyperparameters
    USE_GPU = conf["gpu"]
    NUM_CLASSES = conf["num_classes"]
    BATCH_SIZE = conf["batch_size"]
    EPOCHS = conf["epochs"]
    FINE_TUNE = conf["fine_tune"]
    AUGMENT = conf["augment"]
    PRUNING = conf["pruning"]
    
    # Custom DS
    CUSTOM_DS = conf["custom_ds"]
    CSV_FILE = conf["csv_file"]
    DS_DIR = conf["ds_dir"]
    SPLIT = conf["split"]

    # Run files
    RUN_DIR = conf["run_dir"]

    # Run conf
    NUM_RUNS = conf["num_runs"]
    FAST_DEV_RUN = conf["fast_dev_run"]

else:
    # If there isn't a JSON config, using Fashion MNIST to train
    CUSTOM_DS = None

    # Some hyperparameters
    USE_GPU = args.use_gpu
    NUM_CLASSES = 10
    BATCH_SIZE = args.batch_size
    EPOCHS = args.epochs
    FINE_TUNE = args.fine_tune
    AUGMENT = args.augment
    PRUNING = args.pruning

    # Run files
    RUN_DIR = args.run_dir
    MODEL_CKPT_PATH = RUN_DIR+'models/'
    MODEL_CKPT = 'model-{epoch:02d}-{val_loss:.2f}'

    NUM_RUNS = args.num_runs
    FAST_DEV_RUN = args.fast_dev_run

# Run files pt 2
MODEL_CKPT_PATH = RUN_DIR+'models/'
MODEL_CKPT = 'model-{epoch:02d}-{val_loss:.2f}'

device = set_device(cuda=USE_GPU)
if device.type=="cpu":
    print("Using CPU")
    GPUS = 0
else:
    print("Using GPU")
    GPUS = 1

# Choose which augmentations to use, default uses all
augmentations = {}
if AUGMENT:
    augmentations["random_crop"] = True
    augmentations["random_erasing"] = True
    augmentations["random_perspective"] = True
    augmentations["random_affine"] = True

def train():
    
    ########## Initializing dataset
    custom_ds_info = None
    if CUSTOM_DS:
        custom_ds_info = {
            "csv_file": CSV_FILE,
            "ds_dir": DS_DIR,
            "split": SPLIT
        }

    dm = FashionDataModule(num_classes=NUM_CLASSES, batch_size=BATCH_SIZE, custom_ds_info=custom_ds_info, transforms_args=augmentations, num_workers=4)
    dm.setup()

    ########## Initializing model
    model = ResNet18(num_classes=NUM_CLASSES, fine_tune=FINE_TUNE)

    ########## Initialize logger for tracking and callbacks
    wandb.login()
    wandb_logger = WandbLogger(project='mlops-project', job_type='train', log_model=True)

    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        filename=MODEL_CKPT,
        dirpath=MODEL_CKPT_PATH+wandb_logger.experiment.name,
        save_top_k=3,
        mode='min')

    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        patience=10,
        verbose=True,
        mode='min')

    callbacks = [early_stop_callback, checkpoint_callback]

    if PRUNING:
        pruning_callback = ModelPruning(
            pruning_fn="l1_unstructured", 
            amount=0.1, 
            verbose=1,
            use_global_unstructured=True)
        callbacks.append(pruning_callback)

    callbacks.append(ImagePredictionLogger())

    ########## Training and testing best model
    trainer = pl.Trainer(max_epochs=EPOCHS,
                        gpus = GPUS,
                        auto_lr_find=True,
                        progress_bar_refresh_rate=20,
                        logger=wandb_logger,
                        callbacks=callbacks,
                        checkpoint_callback=True,
                        fast_dev_run=FAST_DEV_RUN)

    trainer.tune(model, datamodule=dm)
    wandb.config.update({"learning_rate": model.learning_rate})
    wandb.config.update(augmentations)
    wandb.config.update({"pruning": PRUNING})
    trainer.fit(model, dm)

    ########### Evaluation
    if not FAST_DEV_RUN:
        trainer.test(ckpt_path="best")
        best_model = trainer.checkpoint_callback.best_model_path

        inference_model = ResNet18.load_from_checkpoint(best_model)
        y_true, y_pred = evaluate(inference_model, dm.test_dataloader(batch_size=BATCH_SIZE, num_workers=4))

        binary_ground_truth = label_binarize(y_true, classes=[i for i in range(NUM_CLASSES)])
        precision_micro, recall_micro, _ = precision_recall_curve(binary_ground_truth.ravel(),
                                                                y_pred.ravel())

        data = [[x, y] for (x, y) in zip(recall_micro, precision_micro)]
        sample_rate = int(len(data)/10000)

        table = wandb.Table(columns=["recall_micro", "precision_micro"], data=data[::sample_rate])
        wandb.log({"precision_recall" : wandb.plot.line(table, 
                                                        "recall_micro", 
                                                        "precision_micro", 
                                                        stroke=None, 
                                                        title="Average Precision")})
        mean_syn, std_syn = measure_inference_time([1, 28, 28], model)
        throughput = measure_throughput([1, 28, 28], model)
        wandb.log({"mean_inference_time" : mean_syn, "std_inference_time" : std_syn}) 
        wandb.log({"inference_per_second" : throughput})
    wandb.finish()

if __name__ == '__main__':
    # Setup folders for saved data
    if not os.path.exists(RUN_DIR):
        os.mkdir(RUN_DIR)

    # Seed for reproducibility
    seed_everything(1234)

    for i in range(NUM_RUNS):
        train()