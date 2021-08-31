
import numpy as np
import random
import torch
import wandb
from pytorch_lightning.callbacks import Callback

def set_seeds(seed=1234):
    """Set seeds for reproducibility."""
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed) # multi-GPU

def set_device(cuda=True):
    """Set device, prioritizing GPU if available"""
    device = torch.device('cuda' if (
        torch.cuda.is_available() and cuda) else 'cpu')
    torch.set_default_tensor_type('torch.FloatTensor')
    if device.type == 'cuda':
        torch.set_default_tensor_type('torch.cuda.FloatTensor')
    return device

def compute_mean_std(loader):
    """Computes mean and std of a dataset over minibatches"""
    
    mean_img = None
    std_img = None

    for imgs, _ in loader:
        if std_img is None:
            std_img = torch.zeros_like(imgs[0])
        if mean_img is None:
            mean_img = torch.zeros_like(imgs[0])
        std_img += ((imgs - mean_img)**2).sum(dim=0)
        mean_img += imgs.sum(dim=0)

    mean_img /= len(loader.dataset)
    std_img /= len(loader.dataset)
    std_img = torch.sqrt(std_img)
    std_img[std_img == 0] = 1
    return mean_img, std_img

def evaluate(model, loader):
    y_true = []
    y_pred = []
    for imgs, labels in loader:
        logits = model(imgs)

        y_true.extend(labels)
        y_pred.extend(logits.detach().numpy())

    return np.array(y_true), np.array(y_pred)

class ImagePredictionLogger(Callback):
    def __init__(self, val_samples, num_samples=32):
        super().__init__()
        self.num_samples = num_samples
        self.val_imgs, self.val_labels = val_samples
        
    def on_validation_epoch_end(self, trainer, pl_module):
        val_imgs = self.val_imgs.to(device=pl_module.device)
        val_labels = self.val_labels.to(device=pl_module.device)
    
        logits = pl_module(val_imgs)
        preds = torch.argmax(logits, -1)
        
        trainer.logger.experiment.log({
            "examples":[wandb.Image(x, caption=f"Pred:{pred}, Label:{y}") 
                        for x, pred, y in zip(val_imgs[:self.num_samples], 
                                                preds[:self.num_samples], 
                                                val_labels[:self.num_samples])]
            })