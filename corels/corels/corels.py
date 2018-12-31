from __future__ import print_function, division
from . import _corels
from .utils import check_consistent_length, check_array
import numpy as np

def get_feature(features, i):
    if not features or abs(i) > len(features):
        return ""

    if i < 0:
        return "not " + features[-i - 1]
    else:
        return features[i - 1]
    
def check_in(name, allowed, val):
    if not val.lower() in allowed:
        allowed_str = "'" + "' '".join(allowed) + "'"
        raise ValueError(name + " must be chosen from " + allowed_str +
                         ", got: " + val)

def check_features(features):
    if not isinstance(features, list):
        raise ValueError("Features must be an list of strings, got: " + str(features))
    
    for i in range(len(features)):
        if not isinstance(features[i], str):
            raise ValueError("Each feature much be a string, got: " + str(features[i]))

def check_rulelist(rules, features, prediction):
    if not isinstance(rules, list):
        raise ValueError("Rulelist must be a list, got: " + str(rules))
    
    if not isinstance(prediction, str):
        raise ValueError("Prediction name must be a string, got: " + str(prediction))

    check_features(features)
    n_features = len(features)

    if len(rules) < 1:
        raise ValueError("Rulelist must contain at least the default rule")

    for r in range(len(rules)):
        if not isinstance(rules[r], dict) or \
           not "prediction" in rules[r] or \
           not "antecedents" in rules[r] or \
           not isinstance(rules[r]["prediction"], (bool, int)) or \
           not isinstance(rules[r]["antecedents"], list): 
            raise ValueError("Bad rule: " + str(rules[r]))
       
        a_len = len(rules[r]["antecedents"])
        for i in range(a_len):
            rule = rules[r]["antecedents"][i]
            if not isinstance(rule, int):
                raise ValueError("Rule id must be an int, got: " + str(rule))
            if abs(rule) > n_features:
                raise ValueError("Rule id out of bounds: " + str(rule))

        if r == (len(rules) - 1) and (a_len != 1 or rules[r]["antecedents"][0] != 0):
            raise ValueError("Last rule in the rulelist must be the default prediction,"
                             " with antecedents '[0]', got: " + str(rules[r]["antecedents"]))

class CorelsClassifier:
    """
    Certifiably Optimal RulE ListS classifier

    [DOC]
    
    Parameters
    ----------
    c : float, optional (default=0.01)
        Regularization parameter. Higher values penalize longer rulelists.

    n_iter : int, optional (default=1000)
        Maximum number of nodes (rulelists) to search before exiting.
    
    map_type : string, optional (default="prefix")
        The type of prefix map to use. Supported maps are "none" for no map,
        "prefix" for a map that uses rule prefixes for keys, "captured" for
        a map with a prefix's captured vector as keys.

    policy : string, optional (default="lower_bound")
        The search policy for traversing the tree (i.e. the criterion with which
        to order nodes in the queue). Supported criteria are "bfs", for breadth-first
        search; "curious", which attempts to find the most promising node; 
        "lower_bound" which is the objective function evaluated with that rulelist
        minus the default prediction error; "objective" for the objective function
        evaluated at that rulelist; and "dfs" for depth-first search.

    verbosity : list, optional (default=["progress"])
        The verbosity levels required. A list of strings, it can contain any
        subset of ["rule", "label", "samples", "progress", "log", "loud"].
        - "rule" prints the a summary for each rule generated.
        - "label" prints a summary of the class labels.
        - "samples" produces a complete dump of the rules and/or label 
            data. "rule" being or "label" must also be already provided.
        - "progress" prints periodic messages as corels runs.
        - "log" prints machine information.
        - "loud" is the equivalent of ["progress", "log", "label", "rule"]
    
    ablation : int, optional (default=0)
        Specifies addition parameters for the bounds used while searching. Accepted
        values are 0 (all bounds), 1 (no antecedent support bound), and 2 (no
        lookahead bound).

    max_card : int, optional (default=2)
        Maximum cardinality allowed when mining rules. Can be any value greater than
        or equal to 1. For instance, a value of 2 would only allow rules that combine
        at most two features in their antecedents.

    min_support : float, optional (default=0.01)
        The fraction of samples that a rule must capture in order to be used. 1 minus
        this value is also the maximum fraction of samples a rule can capture.
        Can be any value between 0.0 and 1.0.
    
    References
    ----------
    Elaine Angelino, Nicholas Larus-Stone, Daniel Alabi, Margo Seltzer, and Cynthia Rudin.
    Learning Certifiably Optimal Rule Lists for Categorical Data. KDD 2017.
    Journal of Machine Learning Research, 2018; 19: 1-77. arXiv:1704.01701, 2017

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.tree import CorelsRegressor
    >>> X = np.array([ [1, 0, 1], [0, 1, 0], [1, 1, 1] ])
    >>> y = np.array([ 1, 0, 1])
    >>> c = CorelsRegressor(verbosity=[])
    >>> c.fit(X, y)
    >>> print(c.predict(X))
    array([ 1, 0, 1 ])
    """

    def __init__(self, c=0.01, n_iter=10000, map_type="prefix", policy="lower_bound",
                 verbosity=["progress"], ablation=0, max_card=2, min_support=0.01):
        self.c = c
        self.n_iter = n_iter
        self.map_type = map_type
        self.policy = policy
        self.verbosity = verbosity
        self.ablation = ablation
        self.max_card = max_card
        self.min_support = min_support
    
    def print(self):
        """
        Print the rulelist in a human-friendly format.
        """

        check_rulelist(self.rules_, self.features_, self.prediction_name)

        if not self.rules_:
            return "Untrained model"
        
        print("\nRULELIST:")
        
        if len(self.rules_) == 1:
            check_rule(self.rules_[0])
            return self.prediction_name + " = " + str(self.rules_[0]["prediction"])
            
        tot = ""
        for i in range(len(self.rules_) - 1):
            feat = get_feature(self.features_, self.rules_[i]["antecedents"][0])
            for j in range(1, len(self.rules_[i]["antecedents"])):
                feat += " && " + get_feature(self.features_, self.rules_[i]["antecedents"][j])
            tot += "if [" + feat + "]:\n  " + self.prediction_name + " = " + str(self.rules_[i]["prediction"]) + "\nelse "

        tot += "\n  " + self.prediction_name + " = " + str(self.rules_[-1]["prediction"])

        print(tot)
        return self

    def fit(self, X, y, features=[], prediction_name="prediction"):
        """
        Build a CORELS classifier from the training set (X, y).

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            The training input samples. All features must be binary, and the matrix
            is internally converted to dtype=np.uint8.

        y : array-line, shape = [n_samples]
            The target values for the training input. Must be binary.
        
        features : list, optional(default=[])
            A list of strings of length n_features. Specifies the names of each
            of the features. If an empty list is provided, the feature names
            are set to the default of ["feature1", "feature2"... ].

        prediction_name : string, optional(default="prediction")
            The name of the feature that is being predicted.

        Returns
        -------
        self : object
        """

        if not isinstance(self.c, float) or self.c < 0.0 or self.c > 1.0:
            raise ValueError("Regularization constant (c) must be a float between"
                             " 0.0 and 1.0, got: " + str(self.c))
        if not isinstance(self.max_nodes, int) or self.max_nodes < 0:
            raise ValueError("Max nodes must be a positive integer, got: " + str(self.max_nodes))
        if not isinstance(self.ablation, int) or self.ablation > 2 or self.ablation < 0:
            raise ValueError("Ablation must be an integer between 0 and 2"
                             ", inclusive, got: " + str(self.ablation))
        if not isinstance(self.map_type, str):
            raise ValueError("Map type must be a string, got: " + str(self.map_type))
        if not isinstance(self.policy, str):
            raise ValueError("Policy must be a string, got: " + str(self.policy))
        if not isinstance(self.verbosity, list):
            raise ValueError("Verbosity must be a list of strings, got: " + str(self.verbosity))
        if not isinstance(self.min_support, float) or self.min_support < 0.0 or self.min_support > 1.0:
            raise ValueError("Minimum support must be a float between"
                             " 0.0 and 1.0, got: " + str(self.min_support))
        if not isinstance(self.max_card, int) or self.max_card < 1:
            raise ValueError("Max cardinality must be an integer greater than or equal to 1"
                             ", got: " + str(self.max_card))
        
        if not isinstance(prediction_name, str):
            raise ValueError("Prediction name must be a string, got: " + str(prediction_name))
       
        check_consistent_length(X, y)
        label = check_array(y, ensure_2d=False, accept_sparse=False, dtype=bool, order='C')
        labels = np.array([ np.invert(label), label ], dtype=np.uint8)
        
        samples = np.array(check_array(X, accept_sparse=False, dtype=bool, order='C'), dtype=np.uint8)

        n_samples = samples.shape[0]
        n_features = samples.shape[1]
        n_labels = labels.shape[0]

        if features:
            check_features(features)
            self.features_ = list(features)
        elif self.features_:
            check_features(self.features_)
        else:
            self.features_ = []
            for i in range(n_features):
                self.features_.append("feature" + str(i + 1))

        if self.features_ and len(self.features_) != n_features:
            raise ValueError("Feature count mismatch between sample data (" + str(n_features) + 
                             ") and feature names (" + str(len(self.features_)) + ")")
        
        self.prediction_name_ = prediction_name

        allowed_verbosities = ["rule", "label", "samples", "progress", "log", "loud"]
        for v in self.verbosity:
            if not isinstance(v, str):
                raise ValueError("Verbosity flags must be strings, got: " + str(v))

            check_in("Verbosities", allowed_verbosities, v)
        
        if "samples" in self.verbosity \
              and "rule" not in self.verbosity \
              and "label" not in self.verbosity:
            raise ValueError("'samples' verbosity option must be combined with at" + 
                             " least one of 'rule' or 'label'")

        # Verbosity for rule mining and minority bound. 0 is quiet, 1 is verbose
        m_verbose = 0
        if "loud" in self.verbosity or "mine" in self.verbosity:
            m_verbose = 1
        
        verbose = ",".join(self.verbosity)

        map_types = ["none", "prefix", "captured"]
        policies = ["bfs", "curious", "lower_bound", "objective", "dfs"]

        check_in("Map type", map_types, self.map_type)
        check_in("Search policy", policies, self.policy)

        map_id = map_types.index(self.map_type)
        policy_id = policies.index(self.policy)

        fr = _corels.fit_wrap_begin(samples, labels, self.features_,
                             self.max_card, self.min_support, verbose, m_verbose, self.c, policy_id,
                             map_id, self.ablation, False)
        
        acc = 0.0
        self.rules_ = []

        if fr:
            while _corels.fit_wrap_loop(self.n_iter):
                pass
        
            self.rules_ = _corels.fit_wrap_end()

        self.is_fitted_ = True

        return self

    def predict(self, X):
        """
        Predict classifications of the input samples X.

        Arguments
        ---------
        X : array-like, shape = [n_samples, n_features]
            The training input samples. All features must be binary, and the matrix
            is internally converted to dtype=np.uint8. The features must be the same
            as those of the data used to train the model.

        Returns
        -------
        p : array of shape = [n_samples].
            The classifications of the input samples.
        """

        check_is_fitted(self, "is_fitted_")
        check_rulelist(self.rules_, self.features_, self.prediction_name)        

        samples = np.array(check_array(X, accept_sparse=False, dtype=bool, order='C'), dtype=np.uint8)
        
        if samples.shape[1] != len(self.features_):
            raise ValueError("Feature count mismatch between eval data (" + str(X.shape[1]) + 
                             ") and feature names (" + str(len(self.features_)) + ")")

        return _corels.predict_wrap(samples, self.rules_)
