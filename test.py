import numpy as np
import corels
import csv

c = corels.CorelsClassifier(verbosity=["mine","progress"], max_nodes=100000000, c=0.01, policy = corels.MAP_PREFIX)

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

print(features)
c.fit(X, y, features=features, max_card=1, min_support=0.01)

print(c)
print("Accuracy: " + str(c.eval(X, y)))
