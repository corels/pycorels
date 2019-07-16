from corels import CorelsClassifier

C = CorelsClassifier(max_card=1, verbosity=["loud", "samples"])

X = [[1, 0, 0], [0, 1, 0], [0, 0, 0], [0, 1, 1]]
y = [1, 0, 1, 1]

C.fit(X, y)
print(C.rl())
