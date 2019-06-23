import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
import numpy as np
from corels import CorelsClassifier

boston = datasets.load_iris()
feature_names = list(boston.feature_names)
X, y = pd.DataFrame(boston.data > 3, columns=feature_names), boston.target

seed = 1
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
print(np.array(X_train))

corels = CorelsClassifier(c=0.0)
score = corels.fit(X_train, y_train).score(X_train, y_train)
corels.printrl()
