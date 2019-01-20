# Pycorels

Welcome to the python binding of the Certifiably Optimal RulE ListS (CORELS) algorithm! For information on CORELS, please visit [our website](https://corels.eecs.harvard.edu).

## Installation

Corels exists on PyPI, and can be downloaded with
`pip install corels`

To install from this repo, simply run `python setup.py install` from the `corels` directory.

## Documentation

The docs for this package are hosted on [our website](https://corels.eecs.harvard.edu/corels/pycorels/)

## Example
~~~~
from corels import *

X, y = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=10000)

a = c.fit(X, y).score(X, y)
print(a)
~~~~
