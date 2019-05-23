import numpy as np
from corels import CorelsClassifier
X = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
y = np.array([ 1, 1, 1])
c = CorelsClassifier(verbosity=[])
c.fit(X, y)
c.printrl()
