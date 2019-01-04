# Pycorels

Welcome to the python binding of the Certifiably Optimal RulE ListS (CORELS) algorithm! For information on CORELS, please visit our [website](https://corels.eecs.harvard.edu).

## Installation

Corels exists on PyPI, and can be downloaded with
`pip install corels`

To install from this repo, simply run `python setup.py install` from the `corels` directory.

## Usage

All functionality is exposed via a class called `CorelsClassifier`. This class has the following methods:

`(constructor)`: Provide data-independent parameters for the classifier   
`fit(X, y)`: Generate a rulelist from the samples `X` and the labels `y`   
`predict(X)`: Predict classifications for the samples `X`   
`score(X, y)`: Score the accuracy of the model on the test samples `X` with labels `y`   

We also provide a helper function called `load_from_csv`, which loads a csv file with binary data
into sample and label datasets (X and y).

## Example
~~~~
from corels import *

X, y = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=10000)

a = c.fit(X, y).score(X, y)
print(a)
~~~~
