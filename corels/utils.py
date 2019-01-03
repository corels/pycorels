import numpy as np

def load_from_csv(fname):
    import csv
    features = []
    prediction_name = ""

    with open(fname, "r") as f:
        features = f.readline().strip().split(",")
        prediction_name = features[-1]
        features = features[0:-1]

    data = np.genfromtxt(fname, dtype=np.uint8, skip_header=1, delimiter=",")

    X = data[:, 0:-1]
    y = data[:, -1]

    return X, y

def check_array(x, ndim=None, dtype=None, order=None):
    if not hasattr(x, 'shape') and \
       not hasattr(x, '__len__') and \
       not hasattr(x, '__array__'):
       raise ValueError("Array must be provided, got: " + str(x))

    x = np.array(x)

    if ndim and ndim != x.ndim:
        raise ValueError("Array must be " + str(ndim) + "-dimensional in shape, got " + str(x.ndim) +
                         " dimensions instead")
    
    if dtype:
        if order:
            return np.array(x, dtype=dtype, order=order)
        return np.array(x, dtype=dtype)
    if order:
        return np.array(x, order=order)
    return x

def check_consistent_length(x, y):
    x = check_array(x)
    y = check_array(y)
    
    if x.ndim < 1 or y.ndim < 1:
        raise ValueError("Arrays must have at least one dimension")

    return x.shape[0] == y.shape[0]

def check_is_fitted(o, n):
    if not hasattr(o, n):
        raise ValueError("Model not fitted yet")

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
