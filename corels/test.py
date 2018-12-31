import numpy as np
import corels
import csv

c = corels.CorelsClassifier(verbosity=["progress"], max_nodes=100000, c=0.01, policy="bfs", map_type="prefix", ablation=1)

""""
nsamples = 100000
nfeatures = 3
X = np.random.randint(2, size=[nsamples, nfeatures], dtype=np.uint8)
y = np.random.randint(2, size=nsamples, dtype=np.uint8)

X = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
y = np.array([ 1, 0, 1])
"""

fname = "compas.csv"
features = []
prediction_name = ""

with open(fname, "r") as f:
    features = f.readline().strip().split(",")
    prediction_name = features[-1]
    features = features[0:-1]

data = np.genfromtxt(fname, dtype=np.uint8, skip_header=1, delimiter=",")

X = data[:, 0:-1]
y = data[:, -1]

c.fit(X, y, features=features, prediction_name=prediction_name, max_card=2, min_support=0.01)

c.rules[0]["prediction"] = 0

print(c)
print("Accuracy: " + str(c.eval(X, y)))
