import argparse
import os
import re
import wandb

from models import *
from data import *
from utils import *

from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelCheckpoint

from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_recall_curve


parser = argparse.ArgumentParser()

parser.add_argument(
    '--data_dir',
    type=str,
    help='Where to store the downloaded dataset',
    default="./data"
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

device = set_device(cuda=args.use_gpu)
if device.type=="cpu":
    print("Using CPU")
else:
    print("Using GPU")

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
MODEL_CKPT_PATH = '/model/'
MODEL_CKPT = '/model/model-{epoch:02d}-{val_loss:.2f}'
NUM_WORKERS = args.num_workers

# Setup folders for saved data
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

if __name__ == '__main__':
    dm = FashionMNISTDataModule(batch_size=BATCH_SIZE, transforms_args=augmentation, num_classes=NUM_CLASSES, val_ratio=VAL_RATIO, data_dir=DATA_DIR, num_workers=NUM_WORKERS)
    dm.setup()

    model = ResNet18(INPUT_SHAPE, NUM_CLASSES)

    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        filename=MODEL_CKPT,
        save_top_k=3,
        mode='min')

    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        patience=3,
        verbose=False,
        mode='min')

    wandb.login()
    wandb_logger = WandbLogger(project='mlops-project', job_type='train')

    trainer = pl.Trainer(max_epochs=EPOCHS,
                        progress_bar_refresh_rate=20,
                        logger=wandb_logger,
                        callbacks=[early_stop_callback,
                                    checkpoint_callback],
                        checkpoint_callback=True)

    trainer.fit(model, dm)
    trainer.test()
    wandb.finish()

    run = wandb.init(project='mlops-project', job_type='producer')

    artifact = wandb.Artifact('model', type='model')
    artifact.add_dir(DATA_DIR+MODEL_CKPT_PATH)

    run.log_artifact(artifact)
    run.join()

    model_ckpts = os.listdir(MODEL_CKPT_PATH)
    losses = []
    for model_ckpt in model_ckpts:
        loss = re.findall("\d+\.\d+", model_ckpt)
        losses.append(float(loss[0]))

    losses = np.array(losses)
    best_model_index = np.argsort(losses)[0]
    best_model = model_ckpts[best_model_index]

    inference_model = ResNet18.load_from_checkpoint(DATA_DIR+MODEL_CKPT_PATH+best_model) if best_model else model
    y_true, y_pred = evaluate(inference_model, dm.test_dataloader())

    binary_ground_truth = label_binarize(y_true,
                                        classes=np.arange(0, 10).tolist())

    precision_micro, recall_micro, _ = precision_recall_curve(binary_ground_truth.ravel(),
                                                            y_pred.ravel())

    run = wandb.init(project='mlops-proj', job_type='evaluate')

    data = [[x, y] for (x, y) in zip(recall_micro, precision_micro)]
    sample_rate = int(len(data)/10000)

    table = wandb.Table(columns=["recall_micro", "precision_micro"], data=data[::sample_rate])
    wandb.log({"precision_recall" : wandb.plot.line(table, 
                                                    "recall_micro", 
                                                    "precision_micro", 
                                                    stroke=None, 
                                                    title="Average Precision")})

    run.join()