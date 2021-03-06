<p align="center">
    <img src="./docs/img/logo.png" alt="TSInterpret Logo" height="300"/>
</p>

TSInterpret is a Python library for interpreting time series classification.
The ambition is to faciliate the usage of times series interpretability methods. The Framework supports Sklearn, Tensorflow, Torch and in some cases predict functions. A listing of implemented algorithms and supported frameworks can be found in our <a href="https://jhoelli.github.io/TSInterpret/AlgorithmOverview/">Documentation</a>.

## 💈 Installation
```shell
pip install TSInterpret
```
You can install the latest development version from GitHub as so:
```shell
pip install https://github.com/jhoelli/TSInterpret.git --upgrade
```

Or, through SSH:
```shell
pip install git@github.com:jhoelli/TSInterpret.git --upgrade
```


## 🍫 Quickstart
The following example creates a simple Neural Network based on tensorflow and interprets the Classfier with Integrated Gradients and Temporal Saliency Rescaling [1].
For further examples check out the <a href="https://jhoelli.github.io/TSInterpret/">Documentation</a>.

[1] Ismail, Aya Abdelsalam, et al. "Benchmarking deep learning interpretability in time series predictions." Advances in neural information processing systems 33 (2020): 6441-6452.

### Import
```python
import pickle
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as snst
from tslearn.datasets import UCR_UEA_datasets
import tensorflow as tf 

```
### Create Classifcation Model
```python

dataset='BasicMotions'
train_x,train_y, test_x, test_y=UCR_UEA_datasets().load_dataset(dataset)
enc1=pickle.load(open(f'../../ClassificationModels/models/{dataset}/OneHotEncoder.pkl','rb'))
train_y=enc1.transform(train_y.reshape(-1,1))
test_y=enc1.transform(test_y.reshape(-1,1))
model_to_explain = tf.keras.models.load_model(f'../../ClassificationModels/models/{dataset}/cnn/{dataset}best_model.hdf5')
```
Explain & Visualize Model
```python
from TSInterpret.InterpretabilityModels.Saliency.SaliencyMethods_TF import Saliency_TF
int_mod=Saliency_TF(model_to_explain, train_x.shape[-2],train_x.shape[-1], method='IG',mode='time')
item= np.array([test_x[0,:,:]])
label=int(np.argmax(test_y[0]))

exp=int_mod.explain(item,labels=label,TSR =True)

%matplotlib inline  
int_mod.plot(np.array([test_x[0,:,:]]),exp)

```
<p align="center">
    <img src="./docs/img/ReadMe.png" alt="Algorithm Results" height="200"/>
</p>

## 🏫 Affiliations
<p align="center">
    <img src="https://upload.wikimedia.org/wikipedia/de/thumb/4/44/Fzi_logo.svg/1200px-Fzi_logo.svg.png?raw=true" alt="FZI Logo" height="200"/>
</p>

## Aknowledgement