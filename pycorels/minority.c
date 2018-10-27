#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <gmp.h>

#include "timer.h"

void usage(char *name)
{
  printf("USAGE: %s out_file label_file minor_file\n", name);
}

mpz_t *sample_array = NULL;

int sample_comp(const void *a, const void *b) {
  return mpz_cmp(sample_array[*(int*)a], sample_array[*(int*)b]);
}

int main(int argc, char **argv)
{
  us_t start = getus();

  if(argc < 4) {
    printf("Please supply a .out, .label, and .minor file\n");
    usage(argv[0]);
    return 1;
  }

  int ret = 0, nrules_raw = 0, nrules = 0, nsamples = 0;
  int *sample_indices = NULL;
  size_t n = 0;
  char *line = NULL, *line_clean = NULL, *minority = NULL;
  FILE *out_fp = NULL, *label_fp = NULL, *minor_fp = NULL;
  mpz_t *rules_vec = NULL;
  mpz_t label0, label1;

  mpz_init(label0);
  mpz_init(label1);

  out_fp = fopen(argv[1], "r");
  if(!out_fp) {
    printf("Could not open .out file\n");
    ret = 1;
    goto end;
  }
  
  label_fp = fopen(argv[2], "r");
  if(!label_fp) {
    printf("Could not open .label file\n");
    ret = 1;
    goto end;
  }

  minor_fp = fopen(argv[3], "w");
  if(!minor_fp) {
    printf("Could not open .minor file\n");
    ret = 1;
    goto end;
  }

  // Get the number of samples and label data
  int label0_set = 0, label1_set = 0;

  while(getline(&line, &n, label_fp) != -1) {
    char *line_cpy = line;
    if(strsep(&line_cpy, "}") && line_cpy[0] == ' ') {
      if(label0_set) {
        if(mpz_set_str(label1, &line_cpy[1], 2) != -1) {
          label1_set = 1;
          break;
        }
      }
      else if(mpz_set_str(label0, &line_cpy[1], 2) != -1)
        label0_set = 1;
    }
  }

  free(line);
  line = NULL;
  n = 0;

  fclose(label_fp);
  label_fp = NULL;

  if(!label0_set || !label1_set) {
    printf("Invalid label file provided\n");
    ret = 2;
    goto end;
  }

  int label0_ones = mpz_sizeinbase(label0, 2);
  int label1_ones = mpz_sizeinbase(label1, 2);

  nsamples = label0_ones > label1_ones ? label0_ones : label1_ones;

  // Get the upper bound on the number of rules in the out file
  int c;
  while(1) {
    c = fgetc(out_fp);

    if(c == '\n')
      nrules_raw++;
    else if(c == EOF) {
      nrules_raw++;
      break;
    }
  }

  rules_vec = malloc(sizeof(mpz_t) * nrules_raw);
  
  rewind(out_fp);

  // Get the rules bitvectors
  while(getline(&line, &n, out_fp) != -1) {
    char *line_cpy = line;
    if(!strsep(&line_cpy, "}") || line_cpy[0] != ' ')
      break;

    mpz_init2(rules_vec[nrules], nsamples);
    if(mpz_set_str(rules_vec[nrules], line_cpy, 2) == -1) {
      mpz_clear(rules_vec[nrules]);
      break;
    }

    nrules++;

    free(line);
    line = NULL;
    n = 0;
  }

  free(line);
  line = NULL;
  n = 0;
    
  line_clean = malloc(nrules + 1);
  sample_array = malloc(sizeof(mpz_t) * nsamples);
  minority = malloc(2 * nsamples + 1);
  sample_indices = malloc(sizeof(int) * nsamples);

  // Generate the sample bitvectors
  for(int s = 0; s < nsamples; s++) {
    for(int i = 0; i < nrules; i++)
      line_clean[i] = !!mpz_tstbit(rules_vec[i], nsamples - s - 1) + '0';

    line_clean[nrules] = '\0';

    mpz_init2(sample_array[s], nrules);
    if(mpz_set_str(sample_array[s], line_clean, 2) == -1) {
      printf("Could not set sample vectors\n");

      for(int k = 0; k <= s; k++)
        mpz_clear(sample_array[k]);
      
      free(sample_array);
      sample_array = NULL;
      ret = 2;
      goto end;
    }
  }

  for(int i = 0; i < nsamples; i++)
    sample_indices[i] = i;
  
  // Sort the samples by value (this groups those samples that are identically featured together)
  qsort(sample_indices, nsamples, sizeof(int), sample_comp);

  // Loop through the sorted samples, finding identically-featured groups
  int begin_group = 0;
  for(int i = 1; i < (nsamples + 1); i++) {
    if(i == nsamples || mpz_cmp(sample_array[sample_indices[i]], sample_array[sample_indices[i-1]]) != 0) {
      int ones = 0;
      int zeroes = 0;
      char c, nc;
      // Find the number of zero-labelled and one-labelled samples in this group
      for(int j = begin_group; j < i; j++) {
        int idx = sample_indices[j];
        if(mpz_tstbit(label0, nsamples - idx - 1))
          zeroes++;
        else
          ones++;
      }

      // What should happen if zeroes = ones??
      // Right now it just replicates bbcache/processing/minority.py
      if(zeroes < ones) {
        c = '1';
        nc = '0';
      }
      else {
        c = '0';
        nc = '1';
      }
      
      // Set all the samples in this group to either 0 or 1 in the minority file
      for(int j = begin_group; j < i; j++) {
        int idx = sample_indices[j];
        if(mpz_tstbit(label0, nsamples - idx - 1)) {
          minority[2 * idx] = c;
          minority[2 * idx + 1] = ' ';
        }
        else {
          minority[2 * idx] = nc;
          minority[2 * idx + 1] = ' ';
        }
      }

      begin_group = i;
    }
  }
  
  minority[2 * nsamples - 1] = '\0';
  fprintf(minor_fp, "{group_minority} %s\n", minority);

end:
  if(out_fp)
    fclose(out_fp);
  if(label_fp)
    fclose(label_fp);
  if(minor_fp)
    fclose(minor_fp);

  if(rules_vec) {
    for(int i = 0; i < nrules; i++)
      mpz_clear(rules_vec[i]);

    free(rules_vec);
  }

  if(line)
    free(line);

  if(line_clean)
    free(line_clean);

  if(sample_array) {
    for(int i = 0; i < nsamples; i++)
      mpz_clear(sample_array[i]);

    free(sample_array);
  }

  if(minority)
    free(minority);

  if(sample_indices)
    free(sample_indices);

  mpz_clear(label0);
  mpz_clear(label1);

  long double diff = (long double)(getus() - start) / (long double)1000000.0;
  printf("Minority bound generation done after %Lf seconds\n", diff);
  
  return ret;
}
