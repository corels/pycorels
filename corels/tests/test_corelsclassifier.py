from corels import CorelsClassifier as C
import corels
import pytest

compas_X, compas_y, compas_features = corels.load_from_csv("../../examples/data/compas.csv")

def test_general_params():
    # Format: name, type, default_value, valid_values, invalid_values, invalid_type_value
    params = [
        ("c", float, 0.01, [0.0, 1.0, 0.01, 0.05, 0.5], [-1.01, 1.01, 100.0], "str"),
        ("n_iter", int, 10000, [0, 1, 1000, 1000000000], [-1, -100], 1.4),
        ("ablation", int, 0, [0, 1, 2], [-1, 3, 100], 1.5),
        ("min_support", float, 0.01, [0.0, 0.25, 0.5], [-0.01, 0.6, 1.5], "str"),
        ("map_type", str, "prefix", ["none", "prefix", "captured"], ["yay", "asdf"], 4),
        ("policy", str, "lower_bound", ["bfs", "curious", "lower_bound", "objective", "dfs"], ["yay", "asdf"], 4),
        ("max_card", int, 2, [1, 2, 10], [0, -1], 1.4),
        ("verbosity", list, ["progress"], [["rule", "label"], ["label"], ["samples"], ["progress", "log", "loud"]], [["whoops"], ["rule", "label", "whoops"]], "str")
    ]

    for param in params:
        # Test constructor default initialization
        c = C()
        assert getattr(c, param[0]) == param[2]
        assert type(getattr(c, param[0])) == param[1]
        
        # Test constructor assignment
        for v in param[3]:
            c = C(**{param[0]: v})
            assert getattr(c, param[0]) == v
            assert type(getattr(c, param[0])) == param[1]

        # Test value errors
        for v in param[4]:
            with pytest.raises(ValueError):
                C(**{param[0]: v}).fit([[1, 0]], [1])
         
        # Test type error
        with pytest.raises(TypeError):
            C(**{param[0]: param[5]}).fit([[1, 0]], [1])
"""        
def test_c():
    rl1 = C(c=0.1).fit(compas_X, compas_y).rl_
    rl2 = C(c=0.01).fit(compas_X, compas_y).rl_
    rl3 = C(c=0.001).fit(compas_X, compas_y).rl_
    
    assert len(rl1.rules) < len(rl2.rules) < len(rl3.rules)
"""
def test_maxcard():
    # Test cardinality cannot be greater than n_features
    C(max_card=3, verbosity=["silent"]).fit([[1, 0, 1], [0, 1, 0]], [0, 1])
    with pytest.raises(ValueError):
        C(max_card=10).fit([[1, 0, 1], [0, 1, 0]], [0, 1])
"""
def test_prediction_name():
    C().fit([[1, 0]], [1], prediction_name="name")
    with pytest.raises(TypeError):
        C().fit([[1, 0]], [1], prediction_name=4)
"""
