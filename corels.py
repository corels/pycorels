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
        self._allowed_verbosities = ["rule", "label", "samples", "progress", "log", "loud"]
        self.features = []
        self.rules = []
    
    def _getfeature(self, i):
        if not self.features or abs(i) >= len(self.features):
            return ""

        if i < 0:
            return "not " + self.features[-i]
        else:
            return self.features[i]

    def __str__(self):
        if not self.rules:
            return "Untrained model"
        
        if len(self.rules) == 1:
            return "predict " + self.rules[0]['prediction']
            
        tot = ""
        for i in range(len(self.rules) - 1):
            feat = self._getfeature(self.rules[i]['antecedents'][0])
            for j in range(1, len(self.rules[i]['antecedents'])):
                feat += " && " + self._getfeature(self.rules[i]['antecedents'][j])
            tot += "if [" + feat + "]:\n  predict " + str(self.rules[i]['prediction']) + "\nelse "

        tot += "\n  predict " + str(self.rules[-1]['prediction'])

        return tot


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

        dfeatures = list(features)

        if not dfeatures:
            dfeatures = []
            for i in range(X.shape[1]):
                dfeatures.append("f" + str(i + 1))
        elif len(dfeatures) != samples.shape[1]:
            raise ValueError("Feature count mismatch between sample data (" + str(samples.shape[1]) + 
                             ") and feature names (" + str(len(dfeatures)) + ")")
        if "samples" in self.verbosity \
              and "rule" not in self.verbosity \
              and "label" not in self.verbosity:
            raise ValueError("'samples' verbosity option must be combined with at" + 
                             " least one of 'rule' or 'label'")

        verbose = ",".join([v for v in self.verbosity if v in self._allowed_verbosities ])
 
        acc, self.rules = libcorels.fit_wrap(samples, labels, dfeatures, max_card, min_support,
                             verbose, mverbose, self.max_nodes, self.c, self.policy,
                             self.map_type, self.log_freq, self.ablation, self.calculate_size)
        
        self.features = dfeatures
        self.features.insert(0, "default")
        
        return acc

    def predict(self, X):
        if not self.features or not self.rules:
            raise ValueError("Model not trained yet")

        samples = np.array(np.array(X, dtype=np.bool), dtype=np.uint8, ndmin=2)
        
        if samples.shape[1] != len(self.features) - 1:
            raise ValueError("Feature count mismatch between eval data (" + str(X.shape[1]) + 
                             ") and feature names (" + str(len(self.features) - 1) + ")")

        return libcorels.predict_wrap(samples, self.features, self.rules)
    
    def eval(self, X, y):
        p = self.predict(X)
        
        labels = np.array(np.array(y, dtype=np.bool), dtype=np.uint8, ndmin=1)

        if p.shape[0] != labels.shape[0]:
            raise ValueError("Number of samples mismatch between sample data (" +
                             p.shape[0] + ") and label data (" + labels.shape[0] + ")")

        acc = np.sum(np.invert(np.logical_xor(p, labels))) / p.shape[0]

        return acc
