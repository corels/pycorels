#ifndef RUN_H
#define RUN_H

#include "rule.h"

#ifdef __cplusplus
extern "C" {
#endif

double run_corels(int max_num_nodes, double c, char* vstring, int curiosity_policy,
                  int map_type, int freq, int ablation, int calculate_size, int nrules, int nlabels,
                  int nsamples, rule_t* rules, rule_t* labels, rule_t* meta, int** rulelist, int* rulelist_size,
                  int** classes);

#ifdef __cplusplus
}
#endif

#endif
