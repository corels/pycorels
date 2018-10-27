#pragma once

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <gmp.h>

#include "rule.h"


PyObject* fill_list(PyObject *obj, rule_t *rules, int start, int nrules, int nsamples);

int load_list(PyObject *list, int *nrules, int *nsamples, rule_t **rules_ret, int add_default_rule);
