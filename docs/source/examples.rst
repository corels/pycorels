Examples
========

Toy Dataset
-----------
::
    
    import numpy as np
    from corels import CorelsClassifier
    X = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
    y = np.array([ 1, 0, 1])
    c = CorelsClassifier(verbosity=[])
    c.fit(X, y)
    print(c.rl())

COMPAS Dataset
--------------
::
    
    from corels import *

    X, y, features = load_from_csv("data/compas.csv")
    c = CorelsClassifier(n_iter=10000)

    a = c.fit(X, y, features=features).score(X, y)
    c.save("model")
    c.load("model")
    print(c.rl())

The data file used in this example can be `found here <https://raw.githubusercontent.com/fingoldin/pycorels/master/tests/data/compas.csv>`_.
