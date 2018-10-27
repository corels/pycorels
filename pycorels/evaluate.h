#pragma once

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "queue.hh"

#include "rule.h"

typedef struct rulelist {
    
    int nrules;
    int *cardinalities;
    char **antecedent_components;
    int *predictions;
    int default_prediction;

} rulelist_t;

int rulelist_init_file(const char *model_file, rulelist_t *out);

void rulelist_free(rulelist_t rulelist);

double evaluate(rulelist_t rulelist, VECTOR *samples, VECTOR *total_captured_correct);
