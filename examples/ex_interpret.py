from corels import *
from interpret import show
from interpret.blackbox import LimeTabular
from interpret.perf import ROC
import time

X, y, features = load_from_csv("data/compas.csv")
c = CorelsClassifier(n_iter=100000)

a = c.fit(X, y, features=features).score(X, y)
print(c.rl())

lime = LimeTabular(predict_fn=c.predict, feature_names=features, data=X)
lime_explain = lime.explain_local(X[:1], y[:1])

show(lime_explain)

time.sleep(100)
