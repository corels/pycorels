from corels import *

X, y = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=100000)

a = c.fit(X, y).score(X, y)

c.printrl()
c.save("model")
c.load("model")
c.printrl()
