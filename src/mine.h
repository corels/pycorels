#ifndef MINE_H
#define MINE_H

#include "rule.h"

int mine_rules(char** features, rule_t *samples, int nfeatures, int nsamples, 
                int max_card, double min_support, rule_t **rules_out, int verbose);

#endif
