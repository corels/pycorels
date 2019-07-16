# Example integration of corels with Microsoft's interpret package (https://github.com/microsoft/interpret)

from corels import *
from interpret import show
from interpret.blackbox import LimeTabular
from interpret.perf import ROC
import time

# Load the compas dataset
X, y, features = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=100000)

# Fit the model. Features is a list of the feature names
a = c.fit(X, y, features=features).score(X, y)
# Print the rulelist
print(c.rl())

# Explain the model's behavior on the first sample. Copy-paste the outputted URL
# into your browser to view the visualization.
lime = LimeTabular(predict_fn=c.predict, feature_names=features, data=X)

show(lime)

time.sleep(100)
