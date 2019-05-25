from corels import *

X, y, features = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=100000)

a = c.fit(X, y, features=features).score(X, y)
c.printrl()
