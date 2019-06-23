import numpy as np
import time
from corels import CorelsClassifier
from interpret import show
from interpret.blackbox import LimeTabular

X = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
y = np.array([ 1, 1, 1])

c = CorelsClassifier(verbosity=[])
c.fit(X, y)
c.printrl()

lime = LimeTabular(predict_fn=c.predict, data=X)
sensitivity_global = lime.explain_local(X[:5], y[:5])

show(sensitivity_global)

time.sleep(100)
