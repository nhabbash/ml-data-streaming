import torch
from torch import nn
import torchvision.models as models
from torchmetrics.functional.classification.accuracy import accuracy

import pytorch_lightning as pl

class ResNet18(pl.LightningModule):
    def __init__(self, input_shape, num_classes, fine_tune=False, learning_rate=2e-4):
        super().__init__()
        
        # log hyperparameters
        self.save_hyperparameters()
        self.learning_rate = learning_rate
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.fine_tune = fine_tune
        
        self.feature_extractor = models.resnet18(pretrained=True)
        self.feature_extractor.conv1 = nn.Conv2d(1, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=True)
        self.feature_extractor.eval()

        for param in self.feature_extractor.parameters():
            param.requires_grad = False
        
        in_features = self.feature_extractor.fc.out_features
        self.classifier = nn.Linear(in_features, num_classes)

        self.loss = nn.CrossEntropyLoss()

        
    def forward(self, x):
        if self.fine_tune:
            x = self.classifier(self.feature_extractor(x))
        else:
            self.feature_extractor.eval()
            with torch.no_grad():
                representations = self.feature_extractor(x)
            x = self.classifier(representations)
        return x

    # logic for a single training step
    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.loss(logits, y)
        
        # training metrics
        preds = torch.argmax(logits, dim=1)
        acc = accuracy(preds, y)
        self.log('train_loss', loss, on_step=True, on_epoch=True, logger=True)
        self.log('train_acc', acc, on_step=True, on_epoch=True, logger=True)
        
        return loss

    # logic for a single validation step
    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.loss(logits, y)

        # validation metrics
        preds = torch.argmax(logits, dim=1)
        acc = accuracy(preds, y)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', acc, prog_bar=True)
        return loss

    # logic for a single testing step
    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.loss(logits, y)
        
        # validation metrics
        preds = torch.argmax(logits, dim=1)
        acc = accuracy(preds, y)
        self.log('test_loss', loss, prog_bar=True)
        self.log('test_acc', acc, prog_bar=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        return optimizer

    