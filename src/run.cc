#include <stdio.h>
#include <iostream>
#include <set>

#include "queue.hh"
#include "run.h"

#define BUFSZ 512

NullLogger* logger;

double run_corels(int max_num_nodes, double c, char* vstring, int curiosity_policy,
                  int map_type, int freq, int ablation, int calculate_size, int nrules, int nlabels,
                  int nsamples, rule_t* rules, rule_t* labels, rule_t* meta, int** rulelist, int* rulelist_size,
                  int** classes)
{
    std::set<std::string> verbosity;

    const char *voptions = "rule|label|samples|progress|log|loud";

    char *vopt = NULL;
    char *vcopy = strdup(vstring);
    while ((vopt = strsep(&vcopy, ",")) != NULL) {
        if (!strstr(voptions, vopt)) {
            fprintf(stderr, "verbosity options must be one or more of (%s)\n", voptions);
            return -1.0;
        }
        verbosity.insert(vopt);
    }
    free(vcopy);

    if (verbosity.count("samples") && !(verbosity.count("rule") || verbosity.count("label"))) {
        fprintf(stderr, "verbosity 'samples' option must be combined with at least one of (rule|label)\n");
        return -1.0;
    }
    
    if (verbosity.count("loud")) {
        verbosity.insert("progress");
        verbosity.insert("log");
    }

    if (verbosity.count("log")) {
        print_machine_info();
    }

    if (verbosity.count("rule")) {
        printf("%d rules %d samples\n\n", nrules, nsamples);
        rule_print_all(rules, nrules, nsamples, verbosity.count("samples"));
        printf("\n\n");
    }

    if (verbosity.count("label")) {
        printf("Labels (%d) for %d samples\n\n", nlabels, nsamples);
        rule_print_all(labels, nlabels, nsamples, verbosity.count("samples"));
        printf("\n\n");
    }
    
    logger = new NullLogger();
    int v = 0;
    if (verbosity.count("loud"))
        v = 1000;
    else if (verbosity.count("progress"))
        v = 1;

    logger->setVerbosity(v);

    double init = timestamp();
    char run_type[BUFSZ];
    Queue* q;
    strcpy(run_type, "LEARNING RULE LIST via ");
    char const *type = "node";
    if (curiosity_policy == 1) {
        strcat(run_type, "CURIOUS");
        q = new Queue(curious_cmp, run_type);
        type = "curious";
    } else if (curiosity_policy == 2) {
        strcat(run_type, "LOWER BOUND");
        q = new Queue(lb_cmp, run_type);
    } else if (curiosity_policy == 3) {
        strcat(run_type, "OBJECTIVE");
        q = new Queue(objective_cmp, run_type);
    } else if (curiosity_policy == 4) {
        strcat(run_type, "DFS");
        q = new Queue(dfs_cmp, run_type);
    } else {
        strcat(run_type, "BFS");
        q = new Queue(base_cmp, run_type);
    }

    PermutationMap* p;
    if (map_type == 1) {
        strcat(run_type, " Prefix Map\n");
        PrefixPermutationMap* prefix_pmap = new PrefixPermutationMap;
        p = (PermutationMap*) prefix_pmap;
    } else if (map_type == 2) {
        strcat(run_type, " Captured Symmetry Map\n");
        CapturedPermutationMap* cap_pmap = new CapturedPermutationMap;
        p = (PermutationMap*) cap_pmap;
    } else {
        strcat(run_type, " No Permutation Map\n");
        NullPermutationMap* null_pmap = new NullPermutationMap;
        p = (PermutationMap*) null_pmap;
    }

    CacheTree* tree = new CacheTree(nsamples, nrules, c, rules, labels, meta, ablation, calculate_size, type);
    if (verbosity.count("progress"))
        printf("%s", run_type);
    // runs our algorithm
    bbound(tree, max_num_nodes, q, p);

    const tracking_vector<unsigned short, DataStruct::Tree>& r_list = tree->opt_rulelist();
    const tracking_vector<bool, DataStruct::Tree>& preds = tree->opt_predictions();

    double accuracy = 1.0 - tree->min_objective() + c*r_list.size();

    *rulelist = (int*)malloc(sizeof(int) * r_list.size());
    *classes = (int*)malloc(sizeof(int) * (1 + r_list.size()));
    *rulelist_size = r_list.size();
    for(size_t i = 0; i < r_list.size(); i++) {
        (*rulelist)[i] = r_list[i];
        (*classes)[i] = preds[i];
    }
    (*classes)[r_list.size()] = preds.back();

    if (verbosity.count("progress")) {
        printf("final num_nodes: %zu\n", tree->num_nodes());
        printf("final num_evaluated: %zu\n", tree->num_evaluated());
        printf("final min_objective: %1.5f\n", tree->min_objective());
        printf("final accuracy: %1.5f\n", accuracy);
        printf("final total time: %f\n", time_diff(init));
    }

    logger->dumpState();
    logger->closeFile();
  
    delete tree;
    delete p;
    delete q;
   
    return accuracy;
}
