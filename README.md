# Clothes Recognizer

## Overview
TODO

# Prerequisites
* Conda 
## Installation
```sh
$ git clone https://github.com/nhabbash/mlops-project
$ cd mlops-project
$ conda env create -f .\environment.yml
```
# Training
```sh
$ cd src
$ python train.py # --help for options
```
# Experiment tracking
* [WandB dashboard](https://wandb.ai/dodicin/mlops-project)
## Structure
The repository is structured as follows:

- [`notebook`](notebook) contains some brief tests and exploration of the model.
- [`src`](src) contains the definitions of the classes needed to train the NN on Fashion MNIST and a suit of unit tests.
- [`demo`](demo) contains the definition of a messagging system leveraging the model. (TODO)

