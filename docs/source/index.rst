.. main-page:

CORELS: Certifiably Optimal RulE ListS
======================================

Welcome to the documentation of the Python binding of CORELS!
All functionality is exposed via a class named 'CorelsClassifier'. In addition, a couple helper functions are provided. Lastly, we provide some examples in the 'examples' section.

Quick Start
--------------
::
    from corels import *
    
    X, y = load_from_csv("compas.csv")

    a = CorelsClassifier().fit(X, y).score(X, y)
    print("Accuracy = " + str(a))

Head over to the `examples page <examples.html>`_ for more code samples.

For installation instructions and more information on the code, visit https://github.com/fingoldin/pycorels.

.. toctree::
    :maxdepth: 2

    CorelsClassifier
    helpers
    examples
