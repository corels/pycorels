#include "mine.h"
#include "timer.h"

#define BUFSZ  1024

// Cycles through all possible permutations of the numbers 1 through n-1 of length r
int getnextperm(int n, int r, int *arr, int first)
{
  // Initialization case
  if(first) {
    for(int i = 0; i < r; i++)
      arr[i] = i;

    return 0;
  }

  for(int i = 1; i < (r + 1); i++) {
    if(arr[r - i] < (n - i)) {
      arr[r - i]++;
      for(int j = (r - i + 1); j < r; j++)
        arr[j] = arr[r - i] + (j - r + i);
      return 0;
    }
  }

  return -1;
}

void mine_rules(char **features, VECTOR *samples, int nfeatures, int nsamples, 
                int max_card, double min_support, mpz_t **rules_out, char ***names_out, int verbose)
{
  us_t start = getus();

  int ntotal_rules = 0, nrules = 0, rule_alloc = 0, rule_alloc_block = 32;
  int *rule_ids = NULL, *rule_names_mine_lengths = NULL;
  char **rule_names = NULL, **rule_names_mine = NULL;
  mpz_t *rules_vec = NULL, *rules_vec_mine = NULL;

  char err[BUFSZ];

  nrules = nfeatures * 2;

  rule_alloc = nrules;
  rules_vec = malloc(sizeof(mpz_t) * rule_alloc);
  rule_names = malloc(sizeof(char*) * rule_alloc);

  rules_vec_mine = malloc(sizeof(mpz_t) * nrules);
  rule_names_mine = malloc(sizeof(char*) * nrules);
  rule_names_mine_lengths = malloc(sizeof(int) * nrules);
 
  for(int i = 0; i < nrules; i++)
    mpz_init2(rules_vec[i], nsamples);

  for(int i = 0; i < nfeatures; i++)
  {
    for(int j = 0; j < nsamples; j++)
    {
      if(mpz_tstbit(samples[j], i)) {
        mpz_setbit(rules_vec[i], j);
        mpz_clrbit(rules_vec[nrules / 2 + i], j);
      }
      else {
        mpz_clrbit(rules_vec[i], j);
        mpz_setbit(rules_vec[nrules / 2 + i], j);
      }
    }
  }

  int min_thresh = min_support * (double)nsamples;
  int max_thresh = (1.0 - min_support) * (double)nsamples;

  // Trimmed number of rules: all rules except those that don't pass the minumum threshold
  int nrules_mine = 0;

  // File rules_vec, the mpz_t version of the rules array
  for(int i = 0; i < nrules; i++) {
    int ones = mpz_popcount(rules_vec[i]);

    // If the rule satisfies the threshold requirements, add it to the out file.
    // If it exceeds the maximum threshold, it is still kept for later rule mining
    // If it less than the minimum threshold, don't add it
    if(ones <= min_thresh) {
      mpz_clear(rules_vec[i]);
      continue;
    }

    mpz_init2(rules_vec_mine[nrules_mine], nsamples);
    mpz_set(rules_vec_mine[nrules_mine], rules_vec[i]);
    
    if(i < (nrules / 2))
      rule_names_mine[nrules_mine] = strdup(features[i]);
    else {
      rule_names_mine[nrules_mine] = malloc(strlen(features[i - (nrules / 2)]) + 5);
      strcpy(rule_names_mine[nrules_mine], features[i - (nrules / 2)]);
      strcat(rule_names_mine[nrules_mine], "-not");
    }

    rule_names_mine_lengths[nrules_mine] = strlen(rule_names_mine[nrules_mine]);
    
    if(ones < max_thresh) {
      memcpy(&rules_vec[ntotal_rules], &rules_vec[i], sizeof(mpz_t));
   
      if(i < (nrules / 2))
        rule_names[ntotal_rules] = strdup(features[i]);
      else {
        rule_names[ntotal_rules] = malloc(strlen(features[i - (nrules / 2)]) + 5);
        strcpy(rule_names[ntotal_rules], features[i - (nrules / 2)]);
        strcat(rule_names[ntotal_rules], "-not");
      }
   
      ntotal_rules++;
      
      if(verbose)
        printf("%s generated with support %f\n", rule_names[nrules_mine], (double)ones / (double)nsamples);
    }
    else
      mpz_clear(rules_vec[i]);

    nrules_mine++;
  }

  mpz_t gen_rule;
  mpz_init2(gen_rule, nsamples);

  rule_str = malloc(nsamples + 2);

  rule_ids = malloc(sizeof(int) * max_card);

  // Generate higher-cardinality rules
  for(int card = 2; card <= max_card; card++) {
    // getnextperm works sort of like strtok
    int r = getnextperm(nrules_mine, card, rule_ids, 1);

    while(r != -1) {
      int valid = 1;
      
      mpz_set(gen_rule, rules_vec_mine[rule_ids[0]]);
      int ones = mpz_popcount(gen_rule);

      // Generate the new rule by successive and operations, and check if it has a valid support
      if(ones > min_thresh) {
        for(int i = 1; i < card; i++) {
          mpz_and(gen_rule, rules_vec_mine[rule_ids[i]], gen_rule);
          ones = mpz_popcount(gen_rule);
          if(ones <= min_thresh) {
            valid = 0;
            break;
          }
        }

        if(valid && ones >= max_thresh)
          valid = 0;
      }
      else
        valid = 0;

      if(valid) {
        ntotal_rules++;

        if(ntotal_rules > rule_alloc) {
          rule_alloc += rule_alloc_block;
          rules_vec = realloc(rules_vec, sizeof(mpz_t) * rule_alloc);
          rule_names = realloc(rule_names, sizeof(char*) * rule_alloc);
        }

        mpz_init2(rules_vec[ntotal_rules - 1], nsamples);
        mpz_set(rules_vec[ntotal_rules - 1], gen_rule);

        int name_len = 0;
        for(int i = 0; i < card; i++)
          name_len += rule_name_mine_lengths[rule_ids[i]] + 1;

        rule_names[ntotal_rules - 1] = malloc(name_len);

        int ch_id = 0;
        for(int i = 0; i < card; i++) {
          for(int j = 0; j < rule_name_mine_lengths[rule_ids[i]]; j++)
            rule_names[ntotal_rules - 1][ch_id + j] = rule_names_mine[rule_ids[i]][j];
          
          ch_id += rule_name_mine_lengths[rule_ids[i]] + 1;

          rule_names[ntotal_rules - 1][ch_id - 1] = ',';
        }

        rule_names[ntotal_rules - 1][ch_id - 1] = '\0';

        if(verbose) {
          putchar('{');
          fputs(rule_names_mine[rule_ids[0]], stdout);
          for(int i = 1; i < card; i++) {
            putchar(',');
            fputs(rule_names_mine[rule_ids[i]], stdout);
          }
          printf("} generated with support %f\n", (double)ones / (double)nsamples);
        }
      }

      r = getnextperm(nrules_mine, card, rule_ids, 0);
    }
  }

  mpz_clear(gen_rule);

  if(rule_ids)
    free(rule_ids);

  if(rules_vec_mine) {
    for(int i = 0; i < nrules_mine; i++)
      mpz_clear(rules_vec_mine[i]);

    free(rules_vec_mine);
  }

  if(rule_names_mine) {
    for(int i = 0; i < nrules_mine; i++)
      free(rule_names_mine[i]);

    free(rule_names_mine);
  }

  if(verbose) {
    printf("Generated %d rules\n", ntotal_rules);

    long double diff = (long double)(getus() - start) / (long double)1000000.0;
    printf("Mining done after %Lf seconds\n", diff);
  }

  *rules_out = rules_vec;
  *names_out = rule_names;

  return NULL;
}
