# Pycorels

Welcome to the python binding of the Certifiably Optimal RulE ListS (CORELS) algorithm! For information on CORELS, please visit [our website](https://corels.eecs.harvard.edu).

## Overview

CORELS (Certifiably Optimal RulE ListS) is a custom discrete optimization technique for building rule lists over a categorical feature space. Using algorithmic bounds and efficient data structures, our approach produces optimal rule lists on practical problems in seconds.

The CORELS pipeline is simple. Given a dataset matrix of size `n_samples x n_features` and a labels vector of size `n_samples`, it will compute a rulelist (similar to a series of if-then statements) to predict the labels with the highest accuracy.

Here's an example:
![Whoops! The image failed to load](https://raw.githubusercontent.com/fingoldin/pycorels/master/utils/Corels.png)

More information about the algorithm [can be found here](https://corels.eecs.harvard.edu/corels)

## Installation

Corels exists on PyPI, and can be downloaded with
`pip install corels`

To install from this repo, simply run `pip install .` or `python setup.py install` from the `corels` directory.

## Documentation

The docs for this package are hosted on [our website](https://corels.eecs.harvard.edu/corels/pycorels/)

## Examples

### Large dataset, loaded from [this file](https://raw.githubusercontent.com/fingoldin/pycorels/master/examples/data/compas.csv)
~~~~
from corels import *

X, y = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=10000)

a = c.fit(X, y).score(X, y)
print(a)
~~~~


