#include <stdio.h>
#include <string.h>
#include <math.h>
#include "mine.h"

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

int mine_rules(char **features, rule_t *samples, int nfeatures, int nsamples, 
                int max_card, double min_support, rule_t **rules_out, int verbose)
{
  int ntotal_rules = 0, nrules = 0, rule_alloc = 0, rule_alloc_block = 32, nrules_mine = 0, ret = 0;
  int *rule_ids = NULL, *rule_names_mine_lengths = NULL;
  rule_t *rules_vec = NULL, *rules_vec_mine = NULL;

  nrules = nfeatures * 2;
  rule_alloc = nrules + 1;
  rules_vec = malloc(sizeof(rule_t) * rule_alloc);
  if(!rules_vec) {
      ret = -1;
      goto end;
  }

  rules_vec_mine = malloc(sizeof(rule_t) * nrules);
  if(!rules_vec_mine) {
      ret = -1;
      goto end;
  }

  rule_names_mine_lengths = malloc(sizeof(int) * nrules);
  if(!rule_names_mine_lengths) {
      ret = -1;
      goto end;
  }
 
  for(int i = 0; i < nrules; i++) {
    if(rule_vinit(nsamples, &rules_vec[i + 1].truthtable) != 0) {
      for(int j = i - 1; j >= 0; j--)
          rule_vfree(&rules_vec[j + 1].truthtable);

      return -1;
    }
  }

  for(int i = 0; i < nfeatures; i++)
  {
    for(int j = 0; j < nsamples; j++)
    {
      if(rule_isset(samples[j].truthtable, i)) {
        rule_set(rules_vec[i + 1].truthtable, j, 1);
        rule_set(rules_vec[nrules / 2 + i + 1].truthtable, j, 0);
      }
      else {
        rule_set(rules_vec[i + 1].truthtable, j, 0);
        rule_set(rules_vec[nrules / 2 + i + 1].truthtable, j, 1);
      }
    }
  }

  int min_thresh = round(min_support * (double)nsamples);
  int max_thresh = round((1.0 - min_support) * (double)nsamples);
  
  // File rules_vec, the mpz_t version of the rules array
  for(int i = 0; i < nrules; i++) {
    int ones = count_ones_vector(rules_vec[i + 1].truthtable, nsamples);
    
    // If the rule satisfies the threshold requirements, add it to the out file.
    // If it exceeds the maximum threshold, it is still kept for later rule mining
    // If it less than the minimum threshold, don't add it
    if(ones <= min_thresh) {
      rule_vfree(&rules_vec[i + 1].truthtable);
      continue;
    }

    if(rule_vinit(nsamples, &rules_vec_mine[nrules_mine].truthtable) != 0) {
        ret = -1;
        goto end;
    }
    rule_copy(rules_vec_mine[nrules_mine].truthtable, rules_vec[i + 1].truthtable, nsamples);
    
    if(i < (nrules / 2)) {
      rules_vec_mine[nrules_mine].features = strdup(features[i]);
      rules_vec_mine[nrules_mine].cardinality = i + 1;
    }
    else {
      rules_vec_mine[nrules_mine].features = malloc(strlen(features[i - (nrules / 2)]) + 5);
      strcpy(rules_vec_mine[nrules_mine].features, features[i - (nrules / 2)]);
      strcat(rules_vec_mine[nrules_mine].features, "-not");
      rules_vec_mine[nrules_mine].cardinality = -(i - (nrules / 2)) - 1;
    }

    rule_names_mine_lengths[nrules_mine] = strlen(rules_vec_mine[nrules_mine].features);
    
    if(ones < max_thresh) {
      memcpy(&rules_vec[ntotal_rules + 1], &rules_vec[i + 1], sizeof(rule_t));
      rules_vec[ntotal_rules + 1].cardinality = 1;
      rules_vec[ntotal_rules + 1].support = ones;
      rules_vec[ntotal_rules + 1].ids = malloc(sizeof(int));
      rules_vec[ntotal_rules + 1].ids[0] = rules_vec_mine[nrules_mine].cardinality;
      rules_vec[ntotal_rules + 1].cardinality = 1;
      rules_vec[ntotal_rules + 1].support = ones;

      if(i < (nrules / 2))
        rules_vec[ntotal_rules + 1].features = strdup(features[i]);
      else {
        rules_vec[ntotal_rules + 1].features = malloc(strlen(features[i - (nrules / 2)]) + 5);
        strcpy(rules_vec[ntotal_rules + 1].features, features[i - (nrules / 2)]);
        strcat(rules_vec[ntotal_rules + 1].features, "-not");
      }
   
      ntotal_rules++;
      
      if(verbose)
        printf("(%d) %s generated with support %f\n", i, rules_vec_mine[nrules_mine].features, (double)ones / (double)nsamples);
    }
    else
      rule_vfree(&rules_vec[i + 1].truthtable);

    nrules_mine++;
  }

  rule_t gen_rule;
  rule_vinit(nsamples, &gen_rule.truthtable);

  rule_ids = malloc(sizeof(int) * max_card);

  // Generate higher-cardinality rules
  for(int card = 2; card <= max_card; card++) {
    // getnextperm works sort of like strtok
    int r = getnextperm(nrules_mine, card, rule_ids, 1);

    while(r != -1) {
      int valid = 1;
      
      rule_copy(gen_rule.truthtable, rules_vec_mine[rule_ids[0]].truthtable, nsamples);
      int ones = count_ones_vector(gen_rule.truthtable, nsamples);

      // Generate the new rule by successive and operations, and check if it has a valid support
      if(ones > min_thresh) {
        for(int i = 1; i < card; i++) {
          rule_vand(gen_rule.truthtable, rules_vec_mine[rule_ids[i]].truthtable, gen_rule.truthtable, nsamples, &ones);
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
          rules_vec = realloc(rules_vec, sizeof(rule_t) * rule_alloc);
        }

        rule_vinit(nsamples, &rules_vec[ntotal_rules].truthtable);
        rule_copy(rules_vec[ntotal_rules].truthtable, gen_rule.truthtable, nsamples);

        int name_len = 0;
        for(int i = 0; i < card; i++)
          name_len += rule_names_mine_lengths[rule_ids[i]] + 1;

        rules_vec[ntotal_rules].features = malloc(name_len);

        int ch_id = 0;
        for(int i = 0; i < card; i++) {
          for(int j = 0; j < rule_names_mine_lengths[rule_ids[i]]; j++)
            rules_vec[ntotal_rules].features[ch_id + j] = rules_vec_mine[rule_ids[i]].features[j];
          
          ch_id += rule_names_mine_lengths[rule_ids[i]] + 1;

          rules_vec[ntotal_rules].features[ch_id - 1] = ',';
        }

        rules_vec[ntotal_rules].features[ch_id - 1] = '\0';
      
        rules_vec[ntotal_rules].cardinality = card;
        rules_vec[ntotal_rules].ids = malloc(sizeof(int) * card);
        for(int k = 0; k < card; k++)
          rules_vec[ntotal_rules].ids[k] = rules_vec_mine[rule_ids[k]].cardinality;

        rules_vec[ntotal_rules].support = ones;

        if(verbose) {
          putchar('{');
          fputs(rules_vec_mine[rule_ids[0]].features, stdout);
          for(int i = 1; i < card; i++) {
            putchar(',');
            fputs(rules_vec_mine[rule_ids[i]].features, stdout);
          }
          printf("} generated with support %f\n", (double)ones / (double)nsamples);
        }
      }

      r = getnextperm(nrules_mine, card, rule_ids, 0);
    }
  }
  
  rules_vec[0].cardinality = 1;
  rules_vec[0].support = nsamples;
  rules_vec[0].ids = malloc(sizeof(int));
  rules_vec[0].ids[0] = 0;
  rules_vec[0].features = malloc(8);
  strcpy(rules_vec[0].features, "default"); 
  make_default(&rules_vec[0].truthtable, nsamples);

  ntotal_rules++;

end:
  rule_vfree(&gen_rule.truthtable);

  if(rule_ids)
    free(rule_ids);

  if(rule_names_mine_lengths)
    free(rule_names_mine_lengths);

  if(rules_vec_mine) {
    for(int i = 0; i < nrules_mine; i++) {
      rule_vfree(&rules_vec_mine[i].truthtable);
      free(rules_vec_mine[i].features);
    }

    free(rules_vec_mine);
  }

  if(verbose)
    printf("Generated %d rules\n", ntotal_rules);

  if (ret == -1) {
    if(rules_vec) {
      for(int i = 0; i < ntotal_rules; i++) {
        rule_vfree(&rules_vec[i + 1].truthtable);
        free(rules_vec[i + 1].features);
      }

      free(rules_vec);
    }
    *rules_out = NULL;
    return -1;
  }
  else {
    *rules_out = rules_vec;
    return ntotal_rules;
  }
}
