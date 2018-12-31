def check_consistent_length(a, b):
    if len(a) != len(b):
        raise ValueError("Size mismatch: " + str(len(a)) + " and " + str(len(b)))

def check_is_fitted(obj, name):
    if not obj[name]:
        raise ValueError("Model not fitted")
