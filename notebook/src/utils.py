
import numpy as np
import torch
import wandb
from pytorch_lightning.callbacks import Callback

def measure_throughput(input_size, model, optimal_batch_size=128):
    # Measuring throughput
    dummy_input = torch.randn([optimal_batch_size]+input_size, dtype=torch.float)
    repetitions=100
    total_time = 0
    with torch.no_grad():
        for rep in range(repetitions):
            starter, ender = torch.cuda.Event(enable_timing=True),   torch.cuda.Event(enable_timing=True)
            starter.record()
            _ = model(dummy_input)
            ender.record()
            torch.cuda.synchronize()
            curr_time = starter.elapsed_time(ender)/1000
            total_time += curr_time
    throughput = (repetitions*optimal_batch_size)/total_time
    return throughput

def measure_inference_time(input_size, model):
    # Measuring inference time
    dummy_input = torch.randn([1]+input_size, dtype=torch.float)

    starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    repetitions = 300
    timings=np.zeros((repetitions,1))
    # GPU warm-up
    for _ in range(10):
        _ = model(dummy_input)
        
    # Measuring
    with torch.no_grad():
        for rep in range(repetitions):
            starter.record()
            _ = model(dummy_input)
            ender.record()
            # GPU Sync
            torch.cuda.synchronize()
            curr_time = starter.elapsed_time(ender)
            timings[rep] = curr_time
    mean_syn = np.sum(timings) / repetitions
    std_syn = np.std(timings)
    return mean_syn, std_syn

def set_device(cuda=True):
    """Set device, prioritizing GPU if available"""
    device = torch.device('cuda' if (torch.cuda.is_available() and cuda) else 'cpu')
    # torch.set_default_tensor_type('torch.FloatTensor')
    # if device.type == 'cuda':
    #     torch.set_default_tensor_type('torch.cuda.FloatTensor')
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
    def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        if batch_idx == 0:
            n = 5
            x, y = batch
        
            wandb.log({'examples': [wandb.Image(x_i, caption=f'Ground Truth: {y_i}\nPrediction: {y_pred}')
                                    for x_i, y_i, y_pred in list(zip(x[:n], y[:n], outputs[:n]))]})