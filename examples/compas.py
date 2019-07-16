from corels import *
import numpy as np

train_proportion = 0.8

X, y, features = load_from_csv("data/compas.csv")
c = CorelsClassifier(max_card=2, n_iter=10000000, verbosity=["loud", "samples"])


train_split = int(train_proportion * X.shape[0])

X_train = X[:train_split]
y_train = y[:train_split]

X_test = X[train_split:]
y_test = y[train_split:]

c.fit(X_train, y_train, features=features)
a = c.score(X_test, y_test)

print("Test Accuracy: ", a)
print(c.rl())
