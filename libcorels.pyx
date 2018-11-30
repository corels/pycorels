from libc.string cimport strdup, strcpy
from libc.stdlib cimport malloc, free
import numpy as np
cimport numpy as np

cdef extern from "corels/src/rule.h":
    ctypedef unsigned long* VECTOR
    cdef struct rule:
        VECTOR truthtable
        char* features
        int cardinality
        int* ids
        int support

    ctypedef rule rule_t
    
    int ascii_to_vector(char *, size_t, int *, int *, VECTOR *)
    void rules_free(rule_t *, const int, int);
    int rule_vfree(VECTOR *)
    int rule_vinit(int, VECTOR *)
    void rule_not(VECTOR, VECTOR, int, int *)
    int rule_isset(VECTOR, int)

cdef extern from "src/run.h":
    double run_corels(int max_num_nodes, double c, char* vstring, int curiosity_policy,
                  int map_type, int freq, int ablation, int calculate_size, int nrules, int nlabels,
                  int nsamples, rule_t* rules, rule_t* labels, rule_t* meta, int** rulelist, int* rulelist_size,
                  int** classes)

cdef extern from "src/mine.h":
    int mine_rules(char **features, rule_t *samples, int nfeatures, int nsamples, 
                int max_card, double min_support, rule_t **rules_out, int verbose)

cdef rule_t* _to_vector(np.ndarray[np.uint8_t, ndim=2] X, int* ncount):
    d0 = X.shape[0]
    d1 = X.shape[1]
    cdef rule_t* vectors = <rule_t*>malloc(d0 * sizeof(rule_t))
    if not vectors:
        raise MemoryError()

    cdef int nones;

    for i in range(d0):
        arrstr = ""
        for j in range(d1):
            arrstr += str(X[i][j])
        
        bytestr = arrstr.encode('ascii')
        if ascii_to_vector(bytestr, len(arrstr), ncount, &nones, &vectors[i].truthtable) != 0:
            for j in range(i):
                rule_vfree(&vectors[j].truthtable)

            free(vectors)
            raise ValueError("Could not load samples")

        vectors[i].ids = NULL
        vectors[i].features = NULL
        vectors[i].cardinality = 1
        vectors[i].support = nones

    return vectors

cdef _free_vector(rule_t* vs, int count):
    if not vs:
        return
    
    for i in range(count):
        rule_vfree(&vs[i].truthtable)
        if vs[i].ids:
            free(vs[i].ids)

        if vs[i].features:
            free(vs[i].features)
    
    free(vs)

cdef _to_nparray(rule_t* X, int nrules, int nsamples):
    arr = np.empty([ nrules, nsamples ], dtype=np.uint8)

    for i in range(nrules):
        for j in range(nsamples):
            arr[i][j] = rule_isset(X[i].truthtable, j)

    return arr

def fit_wrap(np.ndarray[np.uint8_t, ndim=2] samples, 
             np.ndarray[np.uint8_t, ndim=2] labels,
             features, int max_card, double min_support, verbosity_str, int mverbose,
             int max_nodes, double c,
             int policy, int map_type, int log_freq, int ablation,
             int calculate_size):
    cdef int nfeatures = 0
    cdef rule_t* samples_vecs = _to_vector(samples, &nfeatures)

    nsamples = samples.shape[0]

    if nfeatures != len(features):
        _free_vector(samples_vecs, nsamples)
        raise ValueError("Number of features mismatch between sample data and feature names")

    cdef char** features_vec = <char**>malloc(nfeatures * sizeof(char*))
    if not features_vec:
        _free_vector(samples_vecs, nsamples)
        raise MemoryError()

    for i in range(nfeatures):
        bytestr = features[i].encode('ascii')
        features_vec[i] = strdup(bytestr)

    cdef rule_t* rules = NULL

    cdef int r = mine_rules(features_vec, samples_vecs, nfeatures, nsamples,
                max_card, min_support, &rules, mverbose)

    for i in range(nfeatures):
        free(features_vec[i])
    free(features_vec)
    
    _free_vector(samples_vecs, nsamples)

    if r == -1 or rules == NULL:
        raise MemoryError();
    
    out_ids = []
    for i in range(r):
        out_ids.append([])
        for j in range(rules[i].cardinality):
            out_ids[i].append(rules[i].ids[j])

    nrules = r

    verbosity_ascii = verbosity_str.encode('ascii')
    cdef char* verbosity = verbosity_ascii

    cdef int nsamples_chk = 0
    cdef rule_t* labels_vecs = NULL
    try:
        labels_vecs = _to_vector(labels, &nsamples_chk)
    except:
        _free_vector(rules, nrules)
        raise

    if nsamples_chk != nsamples:
        _free_vector(labels_vecs, 2)
        _free_vector(rules, nrules)
        raise ValueError("Sample count mismatch between label and rule data")

    labels_vecs[0].features = <char*>malloc(8)
    labels_vecs[1].features = <char*>malloc(8)
    strcpy(labels_vecs[0].features, "label=0")
    strcpy(labels_vecs[1].features, "label=1")

    cdef int rulelist_size = 0
    cdef int* rulelist = NULL
    cdef int* classes = NULL

    cdef double acc = run_corels(max_nodes, c, verbosity, policy, map_type, log_freq, ablation, calculate_size,
                   nrules, 2, nsamples, rules, labels_vecs, NULL, &rulelist, &rulelist_size, &classes)

    _free_vector(labels_vecs, 2)
    _free_vector(rules, nrules)

    rlist = []
    preds = []
    if rulelist:
        for i in range(rulelist_size):
            rlist.append(rulelist[i])
            preds.append(classes[i])

        preds.append(classes[rulelist_size])
        free(rulelist)
        free(classes)

    return acc, rlist, preds, out_ids
