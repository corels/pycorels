#pragma once

#include <string.h>
#include "rule.h"

void mine_rules(char **features, VECTOR *samples, int nfeatures, int nsamples, 
                int max_card, double min_support, mpz_t **rules_out, char ***names_out, int verbose)
