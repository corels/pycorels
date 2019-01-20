Examples
========

Simple Dataset
--------------

::

    from corels import *

    X, y = load_from_csv("data/compas.csv")
    c = CorelsClassifier(n_iter=10000)

    a = c.fit(X, y).score(X, y)
    print(a)
