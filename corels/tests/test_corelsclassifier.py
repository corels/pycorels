from corels import CorelsClassifier as C
import corels
import pytest
import sys

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
       
def test_set_params():
    c = C()

    r = 0.1
    n_iter = 10
    map_type = "captured"
    policy = "dfs"
    verbosity = ["loud", "samples"]
    ablation = 2
    max_card = 4
    min_support = 0.1

    c.set_params(c=r, n_iter=n_iter, map_type=map_type, policy=policy,
                 verbosity=verbosity, ablation=ablation, max_card=max_card,
                 min_support=min_support)

    assert c.c == r
    assert c.n_iter == n_iter
    assert c.map_type == map_type
    assert c.policy == policy
    assert c.verbosity == verbosity
    assert c.ablation == ablation
    assert c.max_card == c.max_card
    assert c.min_support == c.min_support

    # Test singular assignment
    c.set_params(n_iter=1234)
    assert c.n_iter == 1234

    with pytest.raises(ValueError):
        c.set_params(random_param=4)

def test_c():
    cl = C(verbosity=[], n_iter=100000)
    cs = [0.3, 0.01, 0.0]
    rls = []

    for c in cs:
        cl.set_params(c=c)
        rls.append(cl.fit(compas_X, compas_y).rl_)
    
    for i in range(1, len(rls)):
        assert len(rls[i].rules) > len(rls[i - 1].rules)

def test_maxcard(capfd):
    # Test cardinality cannot be greater than n_features
    with pytest.raises(ValueError):
        C(max_card=10).fit([[1, 0, 1], [0, 1, 0]], [0, 1])

    max_cards = [1, 2, 3]
    nrules = []
    
    # Clear output
    sys.stdout.flush()
    capfd.readouterr()

    for max_card in max_cards:
        C(max_card=max_card, verbosity=["loud"]).fit(compas_X, compas_y)
        sys.stdout.flush()
        
        out = capfd.readouterr().out
        sidx = out.find("Generated ") + 10 
        assert sidx > 9

        fidx = out.find(" ", sidx)
        assert fidx > 0
        
        nrules.append(int(out[sidx:fidx]))

    for i in range(1, len(nrules)):
        assert nrules[i] > nrules[i - 1]

def test_niter(capfd):
    niters = [500, 1000, 2000]
    nnodes = []

    # Clear output
    sys.stdout.flush()
    capfd.readouterr()

    for niter in niters:
        C(n_iter=niter, verbosity=["loud"]).fit(compas_X, compas_y)
        sys.stdout.flush()
        
        out = capfd.readouterr().out
        sidx = out.find("final num_nodes: ") + 17
        assert sidx > 16

        fidx = out.find("\n", sidx)
        assert fidx > 0
        
        nnodes.append(int(out[sidx:fidx]))
    
    for i in range(1, len(nnodes)):
        assert nnodes[i] > nnodes[i - 1]

def test_prediction_name():
    name = "name"
    rname = C(verbosity=[]).fit([[1, 0]], [1], prediction_name=name).rl_.prediction_name
    assert rname == name
    
    rname = C(verbosity=[]).fit([[1, 0]], [1]).rl_.prediction_name
    assert rname == "prediction"

    with pytest.raises(TypeError):
        C().fit([[1, 0]], [1], prediction_name=4)

def test_features():
    assert True
