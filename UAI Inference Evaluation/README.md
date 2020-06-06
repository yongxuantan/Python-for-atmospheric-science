# This set of programs are design for the UAI 2016 Inference Evaluation submission
### Also, it is a class assignment for Dr. Vibhav Gogate's class.
Link to details and submission requirements: http://www.hlt.utdallas.edu/~vgogate/uai16-evaluation/information.html

##### -------------------- Variable-Elimination.py Program details --------------------
Goal: Given Markov network in UAI format, evidence variables and values, compute partition function using min-degree ordering.
```
Language: Python 
Version: 3.6.9
Libraries: os, pandas, numpy, sys

Instructions:
  - The Variable-Elimination.py program reads in 2 arguments in the following order:
    > UAI file path: 			path to UAI file
    > evidence file path: 	path to evidence file

The file references can be direct paths or <filename> if the files are in same directory as the program.
To save console output into a file, append this command to program call " > <filename.ext>".
The PR result will be printed at the end of <filename.ext>.
```

##### -------------------- Cutset-Sampling.py Program details --------------------
Goal: Implement the sampling-based variable elimination algorithm, to compute the probability of evidence or the partition function by combining sampling with variable elimination. Use wCutset to reduce size of a Markov network. Run each algorithm 10 times using different random seeds. For each run, compute the log-relative error between the exact partition function and the approximate one computed by the sampling algorithm.
Data: UAI-files
```
Language: Python 
Version: 3.6.9
Libraries: os, pandas, numpy, sys, functools.reduce, random, math, time

Instructions:
  - The Cutset-Sampling.py program reads in 1 argument as follows:
    > UAI file directory: 			path to all 5 sets of UAI, Evidence, PR files
		
It outputs an excel file to the same directory as program.
To save console output into a file, append this command to program call " > <filename.ext>".
```

##### -------------------- Structural-Learning.py Program details --------------------
Goal: Given a set of I.I.D. sample data files, and a Bayesian network in UAI format that serve as truth, implement these three tasks and output log-likelihood difference:
1. Bayesian network parameter learning algorithm assuming fully observed data and known structure.
2. EM algorithm for learning the parameters of a Bayesian network assuming partially observed data and known structure. Run the EM algorithm for 20 iterations only and repeat for 5 random initializations.
3. Construct k random DAG structures over all variables such that the number of parents of each node is less than or equal to 3. Implement the EM algorithm for learning the parameters of a mixture model. Run the EM algorithm for 20 iterations only and repeat for 5 random ini- tializations. Vary k = 2, 4, 6.

Data: Structural-data-files
- train-f-1.txt to train-f-2.txt are fully observed. 
- train-p-1.txt to train-p-2.txt are partially observed. 
- test.txt is the test data. All variables are binary, they take a value fromthe set {0, 1}.

```
Language: Python 
Version: 3.6.9
Libraries: os, pandas, numpy, sys, random, copy, sys

Instructions:
  - The Structural-Learning.py program reads in 4 argument as follows:
    > UAI file:			path to UAI file
    > Task id:			1, 2, or 3
    > Training data:			path to training data file
	> Test data:			path to test data file
		
It outputs log likelihood difference to console. For task 2 or 3, multiple results are generated for different randomization and K value.
To save console output into a file, append this command to program call " > <filename.ext>".
```
