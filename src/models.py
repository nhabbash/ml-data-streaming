import torch
from torch import nn
import torchmetrics
import torchvision.models as models
import pytorch_lightning as pl

class ResNet18(pl.LightningModule):
    def __init__(self, input_shape, num_classes, learning_rate, fine_tune=False):
        super().__init__()
        
        # log hyperparameters
        self.learning_rate = learning_rate
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.fine_tune = fine_tune
        self.save_hyperparameters()

        self.accuracy = torchmetrics.Accuracy()
        self.loss = nn.CrossEntropyLoss()
        
        #self.quant = torch.quantization.QuantStub()
        #self.dequant = torch.quantization.DeQuantStub()

        self.feature_extractor = models.resnet18(pretrained=True)
        self.feature_extractor.conv1 = nn.Conv2d(1, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=True)

        if not self.fine_tune:
            self.feature_extractor.eval()

            for param in self.feature_extractor.parameters():
                param.requires_grad = False
            
        in_features = self.feature_extractor.fc.out_features
        self.classifier = nn.Linear(in_features, num_classes)
        
    def forward(self, x):
        if self.fine_tune:
            x = self.classifier(self.feature_extractor(x))
        else:
            self.feature_extractor.eval()
            with torch.no_grad():
                x = self.feature_extractor(x)
            x = self.classifier(x)
        return x

    def training_step(self, batch, batch_idx):
        _, loss, acc = self._get_preds_loss_accuracy(batch)

        self.log('train_loss', loss)
        self.log('train_accuracy', acc)
        return loss

    def validation_step(self, batch, batch_idx):
        preds, loss, acc = self._get_preds_loss_accuracy(batch)

        self.log('val_loss', loss)
        self.log('val_accuracy', acc)

        return preds

    def test_step(self, batch, batch_idx):
        _, loss, acc = self._get_preds_loss_accuracy(batch)

        self.log('test_loss', loss)
        self.log('test_accuracy', acc)
    
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        return optimizer

    def _get_preds_loss_accuracy(self, batch):
        x, y = batch
        logits, preds = self.inference(x)
        loss = self.loss(logits, y)
        acc = self.accuracy(preds, y)
        return preds, loss, acc

    def predict(self, x):
        logits = self(x)
        preds = torch.argmax(logits, dim=1)
        return logits, preds