import libcorels
import numpy as np

MAP_NONE           = 0
MAP_PREFIX         = 1
MAP_CAPTURED       = 2

POLICY_BFS         = 0
POLICY_CURIOUS     = 1
POLICY_LOWER_BOUND = 2
POLICY_OBJECTIVE   = 3
POLICY_DFS         = 4

class CorelsClassifier:
    class RuleList:
        def __init__(self, features=[], rules=[], preds=[], ids=[]):
            self.features = features
            self.rules = rules
            self.preds = preds
            self.ids = ids

        def predict(self, X):
            samples = np.array(np.array(X, dtype=np.bool), dtype=np.uint8, ndmin=2)
            
            if samples.shape[1] != len(self.features) - 1:
                raise ValueError("Feature count mismatch between eval data (" + str(X.shape[1]) + 
                                 ") and feature names (" + str(len(self.features) - 1) + ")")

            return libcorels.predict_wrap(samples, self)

        def _getfeature(self, i):
            if i < 0:
                return "not " + self.features[abs(i)]
            else:
                return self.features[i]

        def __str__(self):
            tot = ""
            for i in range(len(self.rules)):
                feat = self._getfeature(self.ids[self.rules[i]][0])
                for j in range(1, len(self.ids[self.rules[i]])):
                    feat += " && " + self._getfeature(self.ids[self.rules[i]][j])
                tot += "if [" + feat + "]:\n  return " + str(self.preds[i]) + "\nelse "

            tot += "\n  return " + str(self.preds[-1])

            return tot

    def __init__(self, c=0.01, max_nodes=10000, map_type=MAP_PREFIX, policy=POLICY_LOWER_BOUND,
                 verbosity=[], ablation=0, calculate_size=False, log="corels-log.txt", log_freq=1000):
        self.c = c
        self.max_nodes = max_nodes
        self.map_type = map_type
        self.policy = policy
        self.verbosity = verbosity
        self.log_freq = log_freq
        self.ablation = ablation
        self.calculate_size = calculate_size
        self.log = log
        self.features = []
        self._allowed_verbosities = ["rule", "label", "samples", "progress", "log", "loud"]

    def fit(self, X, y, features=[], max_card=2, min_support=0.01):
        label = np.array(y, dtype=np.bool)
        labels = np.array([ np.invert(label), label ], dtype=np.uint8, ndmin=2)
        
        samples = np.array(np.array(X, dtype=np.bool), dtype=np.uint8, ndmin=2)

        if samples.shape[0] != labels.shape[1]:
            raise ValueError("Sample count mismatch between sample data (" + str(samples.shape[0]) +
                             ") and label data (" + str(labels.shape[1]) + ")")
        
        mverbose = 0
        if "loud" in self.verbosity or "mine" in self.verbosity:
            mverbose = 1

        if not features:
            features = []
            for i in range(X.shape[1]):
                features.append("f" + str(i + 1))
        elif len(features) != samples.shape[1]:
            raise ValueError("Feature count mismatch between sample data (" + str(samples.shape[1]) + 
                             ") and feature names (" + str(len(features)) + ")")
        if "samples" in self.verbosity \
              and "rule" not in self.verbosity \
              and "label" not in self.verbosity:
            raise ValueError("'samples' verbosity option must be combined with at" + 
                             " least one of 'rule' or 'label'")

        verbose = ",".join([v for v in self.verbosity if v in self._allowed_verbosities ])
 
        acc,rlist,classes,ids = libcorels.fit_wrap(samples, labels, features, max_card, min_support,
                             verbose, mverbose, self.max_nodes, self.c, self.policy,
                             self.map_type, self.log_freq, self.ablation, self.calculate_size)
        
        features.insert(0, "default")

        self.rl = self.RuleList(features, rlist, classes, ids)

        return self.rl

    def predict(self, X):
        if not self.rl:
            raise ValueError("Model not trained yet")

        return self.rl.predict(X)
    
    def eval(self, X, y):
        p = self.rl.predict(X)
        
        labels = np.array(np.array(y, dtype=np.bool), dtype=np.uint8, ndmin=1)

        if p.shape[0] != labels.shape[0]:
            raise ValueError("Number of samples mismatch between sample data (" +
                             p.shape[0] + ") and label data (" + labels.shape[0] + ")")

        acc = np.sum(np.invert(np.logical_xor(p, labels))) / p.shape[0]

        return acc
