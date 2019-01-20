import numpy as np

def print_rulelist(rl):
    """Print a rulelist in a human-friendly format.
    
    Parameters
    ----------
    rl : object
        Rulelist. Usually, you would provide `CorelsClassifier.rl_`, which is of the correct
        format
    """

    check_rulelist(rl)

    print("RULELIST:")
    
    if len(rl.rules) == 1:
        check_rule(rl.rules[0])
        return rl.prediction_name + " = " + str(rl.rules[0]["prediction"])
        
    tot = ""
    for i in range(len(rl.rules) - 1):
        feat = get_feature(rl.features, rl.rules[i]["antecedents"][0])
        for j in range(1, len(rl.rules[i]["antecedents"])):
            feat += " && " + get_feature(rl.features, rl.rules[i]["antecedents"][j])
        tot += "if [" + feat + "]:\n  " + rl.prediction_name + " = " + str(bool(rl.rules[i]["prediction"])) + "\nelse "

    tot += "\n  " + rl.prediction_name + " = " + str(bool(rl.rules[-1]["prediction"]))

    print(tot + "\n")
    
    return rl

def load_from_csv(fname):
    """
    Load a dataset from a csv file.
    
    Parameters
    ----------
    fname : str
        File name of the csv data file
    """

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
    if not hasattr(o, n) or not getattr(o, n):
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

def check_rulelist(rl):
    if not hasattr(rl, "rules") or not hasattr(rl, "features") or not hasattr(rl, "prediction_name"):
        raise ValueError("Rulelist must have the following attributes: 'rules', 'features', 'prediction_name'")

    if not isinstance(rl.rules, list):
        raise ValueError("Rulelist rules must be a list, got: " + str(rl.rules))
    
    if not isinstance(rl.prediction_name, str):
        raise ValueError("Prediction name must be a string, got: " + str(rl.prediction_name))

    check_features(rl.features)
    n_features = len(rl.features)

    if len(rl.rules) < 1:
        raise ValueError("Rulelist must contain at least the default rule")

    for r in range(len(rl.rules)):
        if not isinstance(rl.rules[r], dict) or \
           not "prediction" in rl.rules[r] or \
           not "antecedents" in rl.rules[r] or \
           not isinstance(rl.rules[r]["prediction"], (bool, int)) or \
           not isinstance(rl.rules[r]["antecedents"], list): 
            raise ValueError("Bad rule: " + str(rl.rules[r]))
       
        a_len = len(rl.rules[r]["antecedents"])
        for i in range(a_len):
            rule = rl.rules[r]["antecedents"][i]
            if not isinstance(rule, int):
                raise ValueError("Rule id must be an int, got: " + str(rule))
            if abs(rule) > n_features:
                raise ValueError("Rule id out of bounds: " + str(rule))

        if r == (len(rl.rules) - 1) and (a_len != 1 or rl.rules[r]["antecedents"][0] != 0):
            raise ValueError("Last rule in the rulelist must be the default prediction,"
                             " with antecedents '[0]', got: " + str(rl.rules[r]["antecedents"]))
