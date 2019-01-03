# Pycorels

Welcome to the python binding of the Certifiably Optimal RulE ListS (CORELS) algorithm! For information on CORELS, please visit our [website](https://corels.eecs.harvard.edu).

## Installation

Corels exists on PyPI, and can be downloaded with
`pip install corels`

To install from this repo, simply run `python setup.py install` from the `corels` directory.

## Usage

All functionality is exposed via a class called `CorelsClassifier`.

### pycorels.run

#### Parameters

`pycorels.run` is the most important function, which runs the actual algorithm. Its usage is as follows:

`pycorels.run(out_file, label_file, [keywords])`

Where out_file and label_file can either be file paths (strings) or a list
of tuples, where each tuple contains two elements, the first being a string
for the rule features and the second being a numpy array of ints or bools
of length nsamples, representing the captured bitvector of each rule.

The optional keywords are:

| Keywords                          | Description 
| ---                               | ---
| minor_data (string or list)       | minority info, either in a file path or list
| opt_file (string)                 | the path of the file in which to store the optimal rule list, defaults to "corels-opt.txt"
| log_file (string)                 | the path of the log file, defaults to "corels.txt"
| curiosity_policy (integer)        | the method of ordering the queue elements, valid values are between 0 and 4, inclusive, which correspond to ordering by BFS, curiosity, lower bound, objective, and dfs, respecively
| latex_out (string)                | the path of the file in which to store the output in latex format. Defaults to blank (and no file is outputted unless a path is given)
| map_type (integer)                | the type of symmetry-aware map to use, valid values are between 0 and 2, inclusive, with 0 being no map, 1 being prefix permutation map, and 2 being captured permutation map
| verbosity (string)                | a comma-separated list of verbosity tags, valid tags are 'rule', 'label', 'samples', 'progress', 'log', and 'silent'
| log_freq (integer)                |  every this number of nodes searched in the queue, print an update in the log
| max_num_nodes (integer)           | maximum number of nodes to be searched before exiting
| c (float)                         | regularization constant
| ablation (integer)                | dictates what kind of bounds to use (greater than 1 uses the lower bound on antecedent bound, and greater than 2 uses the lookahead bound)
| calculate_size (bool)             | whether or not the logger should keep track of memory usage

#### Return value

Currently, pycorels.run returns none


### pycorels.tolist

#### Parameters

This function only takes one required argument: a string for the path to
the rule file

#### Return value

returns a list of tuples (in the format detailed above) describing the rules, not containing a default rule

### pycorels.tofile

#### Parameters

This function only takes two required arguments: the first is a list of tuples describing a list of rules (as specified above), and the second is a path to a file. The function then outputs the list into the file specified by the second argument, the exact opposite of pycorels.tolist.

#### Return value

None


## Example

~~~~
import pycorels

pycorels.run("../data/bcancer.out", "../data/bcancer.label", verbosity="progress,samples", max_num_nodes=1000000)

out_list = pycorels.tolist("../data/bcancer.out")
~~~~
