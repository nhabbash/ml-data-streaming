import argparse
import os
import wandb

from models import *
from data import *
from utils import *

from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelPruning
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning import seed_everything

from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_recall_curve

parser = argparse.ArgumentParser()

parser.add_argument(
    '--load_from_json',
    type=str,
    help='Path to a configuration JSON file, will override the other options',
    default=""
)

parser.add_argument(
    '--data_dir',
    type=str,
    help='Where to store the downloaded dataset and the models',
    default="./data/"
)

parser.add_argument(
    '--num_workers',
    type=int,
    default=1,
    help='The number of CPU threads used'
)

parser.add_argument(
    '--random_crop',
    help='Specify if you want to random crop the images',
    type=bool,
    default=True
)

parser.add_argument(
    '--fine_tune',
    help='Fine tune the model instead of training just the last layer',
    type=bool,
    default=False
)

parser.add_argument(
    '--random_erasing',
    help='Specify if you want to randomly erase parts of the images',
    type=bool,
    default=True
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

args = parser.parse_args()

if args.load_from_json != "":
    pass
else:
    device = set_device(cuda=args.use_gpu)
    if device.type=="cpu":
        print("Using CPU")
        GPUS = 0
    else:
        print("Using GPU")
        GPUS = 1

    augmentation = {}
    if args.random_crop:
        augmentation["random_crop"] = True
    if args.random_erasing:
        augmentation["random_erasing"] = True

    NUM_CLASSES = 10
    BATCH_SIZE=args.batch_size
    VAL_RATIO=0.15
    INPUT_SHAPE = [1, 28, 28]
    EPOCHS = args.epochs
    DATA_DIR = args.data_dir
    MODEL_CKPT_PATH = DATA_DIR+'models/'
    MODEL_CKPT = 'model-{epoch:02d}-{val_loss:.2f}'
    NUM_WORKERS = args.num_workers
    FINE_TUNE = args.fine_tune

# Setup folders for saved data
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

if __name__ == '__main__':

    seed_everything(1234)

    # loading data
    dm = FashionMNISTDataModule(batch_size=BATCH_SIZE, transforms_args=augmentation, num_classes=NUM_CLASSES, val_ratio=VAL_RATIO, data_dir=DATA_DIR, num_workers=NUM_WORKERS)
    dm.setup()

    # Initialize logger for tracking
    wandb.login()
    wandb_logger = WandbLogger(project='mlops-project', job_type='train', log_model=True)
    
    # Initializing model
    model = ResNet18(INPUT_SHAPE, NUM_CLASSES, FINE_TUNE)

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
        
    pruning_callback = ModelPruning(
        pruning_fn="l1_unstructured", 
        amount=0.1, 
        verbose=1,
        use_global_unstructured=True)

    # Training
    trainer = pl.Trainer(max_epochs=EPOCHS,
                        gpus = GPUS,
                        auto_lr_find=True,
                        progress_bar_refresh_rate=20,
                        logger=wandb_logger,
                        callbacks=[early_stop_callback,
                                    checkpoint_callback,
                                    #pruning_callback,
                                    ImagePredictionLogger()],
                        checkpoint_callback=True)

    # Experiment identifiers
    run_id = trainer.logger.experiment.id
    project = trainer.logger.experiment.project
    entity = trainer.logger.experiment.entity

    trainer.tune(model, datamodule=dm)
    trainer.fit(model, dm)
    trainer.test(ckpt_path="best")

    # Evaluating
    best_model = trainer.checkpoint_callback.best_model_path

    inference_model = ResNet18.load_from_checkpoint(best_model)
    y_true, y_pred = evaluate(inference_model, dm.test_dataloader())

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