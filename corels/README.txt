Welcome to the python binding of the Certifiably Optimal RulE ListS (CORELS) algorithm! 

This class implements the CORELS algorithm, designed to produce human-interpretable, optimal
rulelists for binary feature data and binary classification. As an alternative to other
tree based algorithms such as CART, CORELS provides a certificate of optimality for its 
rulelist given a training set, leveraging multiple algorithmic bounds to do so.

In order to use run the algorithm, create an instance of the `CorelsClassifier` class, 
providing any necessary parameters in its constructor, and then call `fit` to generate
a rulelist. `print_list` prints the generated rulelist, while `predict` provides
classification predictions for a separate test dataset with the same features. To determine 
the algorithm's accuracy, run `score` on an evaluation dataset with labels.

For information on CORELS, please visit our website: https://corels.eecs.harvard.edu.
