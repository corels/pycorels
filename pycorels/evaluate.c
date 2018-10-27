#include "evaluate.hh"

#ifdef GMP

void randomize_data(data_t* data, gmp_randstate_t state)
{
    for(int i = 1; i < data->nrules; i++) {
        randomize_rule(&data->rules[i], data->nsamples, state);
    }

    randomize_rule(&data->labels[0], data->nsamples, state);

    mpz_com(data->labels[1].truthtable, data->labels[0].truthtable);

    mpz_t tmp;
    mpz_init2(tmp, data->nsamples);
    mpz_ui_pow_ui(tmp, 2, data->nsamples);
    mpz_sub_ui(tmp, tmp, 1);

    mpz_and(data->labels[1].truthtable, data->labels[1].truthtable, tmp);

    mpz_clear(tmp);
}

void randomize_rule(rule_t* rule, int nsamples, gmp_randstate_t state)
{
    mpz_rrandomb(rule->truthtable, state, nsamples);
    rule->support = mpz_popcount(rule->truthtable);
}

#else

void randomize_data(data_t* data)
{
    for(int i = 1; i < data->nrules; i++) {
        randomize_rule(&data->rules[i], data->nsamples);
    }

    randomize_rule(&data->labels[0], data->nsamples);

    // TODO: Fix so that extra bits in the last v_entriy don't get set
    int temp;
    rule_not(data->labels[1].truthtable, data->labels[0].truthtable, data->nsamples, &temp);
}

void randomize_rule(rule_t* rule, int nsamples)
{
    int nentries = (nsamples + BITS_PER_ENTRY - 1)/BITS_PER_ENTRY;

    // TODO: Fix so that extra bits don't get set
    int count = 0;
    for(int i = 0; i < nentries; i++) {
        rule->truthtable[i] = (double)(~(v_entry)0) * (double)rand() / (double)RAND_MAX;
        count += count_ones(rule->truthtable[i]);
    }

    rule->support = count;
}

#endif

double obj_brute(data_t data, rulelist_t* opt_list, int max_list_len, double c, int v)
{
    double min_obj = 1.0;

    max_list_len = max_list_len > data.nrules-1 ? data.nrules-1 : max_list_len;

    int max_len = (int)(1.0 / c);

    max_list_len = max_list_len > max_len ? max_list_len : max_len;

    rulelist_t temp_list;
    // Temp info, used when calculating each rule list
    temp_list.ids = (unsigned short*)malloc(sizeof(unsigned short) * max_list_len);
    temp_list.predictions = (int*)malloc(sizeof(int) * max_list_len);
    temp_list.nrules = 0;

    if(opt_list) {
        opt_list->ids = (unsigned short*)malloc(sizeof(unsigned short) * max_list_len);
        opt_list->predictions = (int*)malloc(sizeof(int) * max_list_len);
        opt_list->default_prediction = 0;
        opt_list->nrules = 0;
    }

    for(int i = 0; i < 2; i++) {
        temp_list.default_prediction = i;

        temp_list.nrules = 0;
        double obj = evaluate_data(data, temp_list, NULL, c, v ? 1 : 0);

        if(obj == -1.0)
            continue;

        if(obj < min_obj) {
            if(v > 2)
                printf("[obj_brute] min obj:  %f -> %f\n", min_obj, obj);

            if(opt_list) {
                opt_list->nrules = 0;
                opt_list->default_prediction = temp_list.default_prediction;
            }
            min_obj = obj;
        }

        if(max_list_len)
            _obj_brute_helper(data, &min_obj, opt_list, temp_list, max_list_len, c, v);
    }

    if(v > 1) {
        printf("[obj_brute]: Optimal objective: %f\n", min_obj);
    }

    rulelist_free(temp_list);

    return min_obj;
}

void _obj_brute_helper(data_t data, double* min_obj, rulelist_t* opt_list, rulelist_t prefix, int max_list_len, double c, int v) {
    for(int rule_id = 1; rule_id < data.nrules; rule_id++) {
        int found = 0;

        for(int i = 0; i < prefix.nrules; i++) {
            if(prefix.ids[i] == rule_id) {
                found = 1;
                break;
            }
        }

        if(found)
            continue;

        for(int label = 0; label < 2; label++) {
            prefix.ids[prefix.nrules] = rule_id;
            prefix.predictions[prefix.nrules] = label;
            prefix.nrules = prefix.nrules + 1;

            double obj = evaluate_data(data, prefix, NULL, c, v ? 1 : 0);

            if(obj == -1.0) {
                if(v > 0)
                    printf("[obj_brute_helper] Error evaluating a rule list!\n");
                return;
            }

            if(obj < *min_obj) {
                if(v > 2)
                    printf("[obj_brute_helper] min obj:  %f -> %f\n", *min_obj, obj);

                if(opt_list) {
                    memcpy(opt_list->ids, prefix.ids, sizeof(unsigned short) * prefix.nrules);
                    memcpy(opt_list->predictions, prefix.predictions, sizeof(int) * prefix.nrules);
                    opt_list->default_prediction = prefix.default_prediction;
                    opt_list->nrules = prefix.nrules;
                }
                *min_obj = obj;
            }

            if(prefix.nrules < max_list_len)
                _obj_brute_helper(data, min_obj, opt_list, prefix, max_list_len, c, v);
        }
    }
}

int data_init_model(rulelist_t* out, data_t data, const char* model_file, int v)
{
    FILE* model_p = NULL;
    if((model_p = fopen(model_file, "r")) == NULL) {
        if(v > 0)
            printf("[data_init_model] Error opening model file at path '%s'\n", model_file);
        return 1;
    }

    fseek(model_p, 0L, SEEK_END);
    long size = ftell(model_p);
    rewind(model_p);

    char* buffer = (char*)malloc(sizeof(char) * (size + 1));

    long r = fread(buffer, sizeof(char), size, model_p);
    if(r != size) {
        if(v > 0)
            printf("[data_init_model] Error reading model file at path '%s'\n", model_file);
        free(buffer);
        fclose(model_p);
        return 1;
    }
    buffer[size] = '\0';

    fclose(model_p);

    char* prev_rule_loc = buffer - 1;
    char* rule_loc = NULL;
    int nrules = 0;
    int default_pred = 0;

    out->ids = (unsigned short*)malloc(sizeof(unsigned short));
    out->predictions = (int*)malloc(sizeof(int));

    while((rule_loc = strchr(prev_rule_loc + 1, '~')) != NULL) {

        char* feature_start = prev_rule_loc + 3;
        if(prev_rule_loc == (buffer - 1))
            feature_start = buffer;

        int feature_len = (rule_loc - feature_start);

        if(strncmp("default", feature_start, feature_len) == 0) {
            default_pred = *(rule_loc + 1) - '0';
            break;
        }
        else {
            int found = 0;

            for(int i = 1; i < data.nrules; i++) {
                if(strncmp(data.rules[i].features, feature_start, feature_len) == 0) {
                    if(++nrules >= data.nrules) {
                        if(v > 0)
                            printf("[data_init_model] Error: rule number overflow\n");
                        free(out->ids);
                        out->ids = NULL;
                        free(out->predictions);
                        out->predictions = NULL;
                        free(buffer);
                        return 1;
                    }

                    found = 1;

                    out->ids = (unsigned short*)realloc(out->ids, sizeof(unsigned short) * nrules);
                    out->predictions = (int*)realloc(out->predictions, sizeof(int) * nrules);

                    out->ids[nrules-1] = i;
                    out->predictions[nrules-1] = *(rule_loc + 1) - '0';

                    break;
                }
            }

            if(!found) {
                if(v > 0)
                    printf("[data_init_model] Error: could not find rule with features '%.*s'\n", feature_len, feature_start);
                free(out->ids);
                out->ids = NULL;
                free(out->predictions);
                out->predictions = NULL;
                free(buffer);
                return 1;
            }
        }

        prev_rule_loc = rule_loc;
    }

    free(buffer);

    out->nrules = nrules;
    out->default_prediction = default_pred;

    return 0;
}

int data_init(data_t* out, rulelist_t* opt_out, const char* model_file, const char* out_file, const char* label_file, int v)
{
    if(rules_init(out_file, &out->nrules, &out->nsamples, &out->rules, 1) != 0) {
        if(v > 0)
            printf("[data_init] Error reading .out file at path '%s'\n", out_file);
        return 1;
    }

    int nsamples_chk, nlabels;
    if(rules_init(label_file, &nlabels, &nsamples_chk, &out->labels, 0) != 0) {
        if(v > 0)
            printf("[data_init] Error reading .label file at path '%s'\n", label_file);
        rules_free(out->rules, out->nrules, 1);
        return 1;
    }

    if(nlabels != 2) {
        if(v > 0)
            printf("[data_init] Error: The .label file at path '%s' does not contain exactly 2 labels", label_file);

        rules_free(out->rules, out->nrules, 1);
        rules_free(out->labels, nlabels, 0);
    }

    /*if(out->nsamples != nsamples_chk) {
        if(v > 0)
            printf("[data_init] Error: Nsamples mismatch between .out and .label files\n");

        rules_free(out->rules, out->nrules, 1);
        rules_free(out->labels, 2, 0);
        return 1;
    }*/

    if(model_file != NULL) {
        return data_init_model(opt_out, *out, model_file, v);
    }

    return 0;
}

void data_free(data_t data)
{
    if(data.rules)
        rules_free(data.rules, data.nrules, 1);

    if(data.labels)
        rules_free(data.labels, 2, 0);
}

void rulelist_free(rulelist_t rulelist)
{
    if(rulelist.ids)
        free(rulelist.ids);

    if(rulelist.predictions)
        free(rulelist.predictions);
}


double evaluate(const char * model_file, const char *out_file, const char *label_file, VECTOR *total_captured_correct, double c, int v)
{
    data_t data;
    rulelist_t opt_list;

    if(data_init(&data, &opt_list, model_file, out_file, label_file, v) != 0) {
        printf("[evaluate] Error loading model, exiting\n");
        return -1.0;
    }

    double r = evaluate_data(data, opt_list, total_captured_correct, c, v);

    data_free(data);
    rulelist_free(opt_list);

    return r;
}

double evaluate_data(data_t data, rulelist_t list, VECTOR *total_captured_correct, double c, int v)
{
    //printf("%d\n", model.nrules);

    VECTOR total_captured;
    rule_vinit(data.nsamples, &total_captured);

    int total_ncaptured = 0;
    int total_nincorrect = 0;

    // model.nrules doesn't include the default rule
    for(int i = 0; i < list.nrules; i++) {
        rule_t rule = data.rules[list.ids[i]];
        int pred = list.predictions[i];

        int len = i + 1;

        VECTOR captured, captured_correct;
        rule_vinit(data.nsamples, &captured);
        rule_vinit(data.nsamples, &captured_correct);

        int ncaptured, ncorrect, temp;

        // Get which ones are captured by the current rule
        rule_vandnot(captured, rule.truthtable, total_captured, data.nsamples, &ncaptured);
        rule_vor(total_captured, total_captured, captured, data.nsamples, &temp);

        total_ncaptured += ncaptured;

        rule_vand(captured_correct, captured, data.labels[pred].truthtable, data.nsamples, &ncorrect);

        if(total_captured_correct) {
            int temp;
            rule_vor(*total_captured_correct, *total_captured_correct, captured_correct, data.nsamples, &temp);
        }

        total_nincorrect += (ncaptured - ncorrect);

        if(v > 2) {
            VECTOR default_correct;
            int ndefault_correct;
            rule_vinit(data.nsamples, &default_correct);

            double lower_bound = (double)total_nincorrect / (double)data.nsamples + (double)len * c;

            rule_vandnot(default_correct, data.labels[list.default_prediction].truthtable, total_captured, data.nsamples, &ndefault_correct);

            double objective = lower_bound + (double)(data.nsamples - total_ncaptured - ndefault_correct) / (double)data.nsamples;

            printf("[evaluate_data] Rule #%d (id: %d, prediction: %s) processed:\n" \
                   "[evaluate_data]     ncaptured: %d    ncaptured correctly: %d (%.1f%%)    lower bound: %.6f    objective: %.6f\n\n",
                   i+1, list.ids[i], pred ? "true" : "false",
                   ncaptured, ncorrect, 100.0 * (double)ncorrect / (double)ncaptured, lower_bound, objective);

            rule_vfree(&default_correct);
        }

        rule_vfree(&captured);
        rule_vfree(&captured_correct);
    }

    VECTOR default_correct;
    int ndefault_correct;

    rule_vinit(data.nsamples, &default_correct);
    rule_vandnot(default_correct, data.labels[list.default_prediction].truthtable, total_captured, data.nsamples, &ndefault_correct);

    if(total_captured_correct) {
        int temp;
        rule_vor(*total_captured_correct, *total_captured_correct, default_correct, data.nsamples, &temp);
    }

    rule_vfree(&default_correct);

    total_nincorrect += (data.nsamples - total_ncaptured - ndefault_correct);

    double incorrect_frac = (double)total_nincorrect / (double)data.nsamples;

    double objective = incorrect_frac + (double)list.nrules * c;

    if(v > 1) {
        int ndefault_captured = data.nsamples - total_ncaptured;
        printf("[evaluate_data] Default rule (prediction: %s) processed:\n" \
               "[evaluate_data]     ncaptured: %d    ncaptured correctly: %d (%.1f%%)\n\n",
               list.default_prediction ? "true" : "false",
               ndefault_captured, ndefault_correct, 100.0 * (double)ndefault_correct / (double)ndefault_captured);

        printf("\n[evaluate_data] Final results:\n" \
               "[evaluate_data]     objective: %.10f    nsamples: %d    total captured (excluding default): %d    total incorrect: %d (%.3f%%)    accuracy: %.3f%%\n",
               objective, data.nsamples, total_ncaptured, total_nincorrect, 100.0 * incorrect_frac, 100.0 - 100.0 * incorrect_frac);
    }

    return objective;
}

void output_error(data_t data, tracking_vector<unsigned short, DataStruct::Tree> corels_opt_list,
                  tracking_vector<bool, DataStruct::Tree> corels_opt_preds,
                  tracking_vector<unsigned short, DataStruct::Tree> brute_opt_list,
                  tracking_vector<bool, DataStruct::Tree> brute_opt_preds, bool output_brute, double corels_obj,
                  double eval_check_obj, double brute_obj, int v)
{
    printf("\n\n\n\n/***************************************************************/\n\n");
    printf("Errors were detected in the following set of data:\n\n");

    printf("Dumping rule data:\n");
    for(int i = 0; i < data.nrules; i++) {
        rule_print(data.rules, i, data.nsamples, 1);
    }

    printf("\nDumping label data:\n");
    for(int i = 0; i < 2; i++) {
        rule_print(data.labels, i, data.nsamples, 1);
    }

    printf("\n\nOptimal rule list determined by CORELS:\n");
    print_final_rulelist(corels_opt_list, corels_opt_preds, NULL, data.rules, data.labels, NULL, 1);

    if(output_brute) {
        printf("\nOptimal rule list determined by brute force:\n");
        print_final_rulelist(brute_opt_list, brute_opt_preds, NULL, data.rules, data.labels, NULL, 1);

        printf("\nOptimal objective determined by CORELS: %f\n" \
               "Objective of optimal rule list determined by CORELS: %f\n" \
               "Optimal objective determined by brute-force: %f\n\n",
               corels_obj, eval_check_obj, brute_obj);
    }
    else {
        printf("\nOptimal objective determined by CORELS: %f\n" \
               "Objective of optimal rule list determined by CORELS: %f\n\n",
               corels_obj, eval_check_obj);
    }
}

int run_random_tests(size_t num_iters, int num_rules, int num_samples, double c, int b_max_list_len,
                     int ablation, std::function<bool(Node*, Node*)> q_cmp, const char* node_type, bool useCapturedPMap,
                     size_t max_num_nodes, double epsilon, unsigned long seed, int v)
{
    data_t data;

    data.nrules = num_rules;
    data.nsamples = num_samples;

    data.rules = (rule_t*)malloc(sizeof(rule_t) * data.nrules);
    data.labels = (rule_t*)malloc(sizeof(rule_t) * 2);

    for(int i = 1; i < data.nrules; i++) {
        rule_vinit(data.nsamples, &data.rules[i].truthtable);
        data.rules[i].support = 0;
        data.rules[i].cardinality = 1;

        char number[64];
        sprintf(number, "%d", i);

        int numlen = strlen(number);
        data.rules[i].features = (char*)malloc(sizeof(char) * (numlen + 7));

        strcpy(data.rules[i].features, "{rule");
        strcat(data.rules[i].features, number);
        strcat(data.rules[i].features, "}");
    }

    // Default rule
    rule_vinit(data.nsamples, &data.rules[0].truthtable);
    make_default(&data.rules[0].truthtable, data.nsamples);

    data.rules[0].support = data.nsamples;
    data.rules[0].cardinality = 1;

    data.rules[0].features = (char*)malloc(sizeof(char) * 8);
    strcpy(data.rules[0].features, "default");


    for(int i = 0; i < 2; i++) {
        rule_vinit(data.nsamples, &data.labels[i].truthtable);
        data.labels[i].support = 0;
        data.labels[i].cardinality = 1;

        char number[64];
        sprintf(number, "%d", i);

        int numlen = strlen(number);
        data.labels[i].features = (char*)malloc(sizeof(char) * (numlen + 9));

        strcpy(data.labels[i].features, "{label=");
        strcat(data.labels[i].features, number);
        strcat(data.labels[i].features, "}");
    }

    int returnCode = 0;

#ifdef GMP
    gmp_randstate_t rand_state;

    gmp_randinit_mt(rand_state);

    gmp_randseed_ui(rand_state, seed);
#else
    srand(seed);
#endif

    bool exit = false;
    for(size_t i = 0; i < num_iters && !exit; i++)
    {
#ifdef GMP
        randomize_data(&data, rand_state);
#else
        randomize_data(&data);
#endif

        PermutationMap* p;
        if(useCapturedPMap)
            p = new CapturedPermutationMap();
        else
            p = new PrefixPermutationMap();

        CacheTree* tree = new CacheTree(data.nsamples, data.nrules, c, data.rules, data.labels, NULL, ablation, false, node_type);
        Queue* q = new Queue(q_cmp, "run type");

        // Run CORELS
        bbound(tree, max_num_nodes, q, p);
        double c_obj = tree->min_objective();

        // Evaluate CORELS objective to make sure it corresponds to the correct rule list outputted as well
        tracking_vector<unsigned short, DataStruct::Tree> opt_list = tree->opt_rulelist();
        tracking_vector<bool, DataStruct::Tree> opt_preds = tree->opt_predictions();
        tracking_vector<int, DataStruct::Tree> opt_preds_int(opt_preds.begin(), opt_preds.end());

        rulelist_t rlist;
        rlist.nrules = opt_list.size();
        rlist.ids = &opt_list[0];
        rlist.predictions = &opt_preds_int[0];
        rlist.default_prediction = opt_preds_int[rlist.nrules];

        // Check objective outputted by CORELS
        double e_obj = evaluate_data(data, rlist, NULL, c, v);

        tracking_vector<unsigned short, DataStruct::Tree> b_opt_list;
        tracking_vector<bool, DataStruct::Tree> b_opt_preds;

        double b_obj = c_obj;
        if(b_max_list_len) {
            rulelist_t b_rlist;

            // Find optimal rulelist by brute force
            b_obj = obj_brute(data, &b_rlist, b_max_list_len, c, v);

            // Get optimal rule list info generated by brute force
            b_opt_list.assign(b_rlist.ids, b_rlist.ids + b_rlist.nrules);
            b_opt_preds.assign(b_rlist.predictions, b_rlist.predictions + b_rlist.nrules);
            b_opt_preds.push_back(b_rlist.default_prediction);

            rulelist_free(b_rlist);
        }

        if(e_obj == -1.0) {
            if(v > 0)
                printf("[main] Error with evaluation calculations! Exiting\n");

            returnCode = 2;
            exit = true;
        }


        if(b_max_list_len && b_obj == -1.0) {
            if(v > 0)
                printf("[main] Error with objective calculations! Exiting\n");

            returnCode = 2;
            exit = true;
        }

        double d = c_obj - e_obj;
        double d1 = c_obj - b_obj;
        double e = epsilon;

        // Check if brute force obj >= CORELS obj and if CORELS obj = evaluate obj
        if(d1 > e || d > e || d < -e) {
            if(v > 1) {
                printf("[main] Mismatch detected, logging and exiting\n");
            }

            output_error(data, opt_list, opt_preds, b_opt_list, b_opt_preds, (bool)b_max_list_len, c_obj, e_obj, b_obj, v);

            returnCode = 1;
            exit = true;
        }


        delete p;

        if(c_obj == 0.0)
            tree->insert_root();

        delete tree;
        delete q;
    }

    data_free(data);

#ifdef GMP
    gmp_randclear(rand_state);
#endif

    return returnCode;
}
