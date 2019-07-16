from corels import CorelsClassifier

C = CorelsClassifier(max_card=2, c=0.0, verbosity=["loud", "samples"])

X = [[1, 0, 1], [0, 0, 0], [1, 1, 0], [0, 1, 0]]
y = [1, 0, 0, 1]
features = ["Mac User", "Likes Pie", "Age < 20"]

C.fit(X, y, features=features, prediction_name="Has a dirty computer")
print(C.rl())
