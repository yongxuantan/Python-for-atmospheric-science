### Program: BinaryDecisionTree.py
### Language: Python 
- Version: 3.6.5
- Libraries: pandas, math, random, copy, sys
### Written by: Yours truly
#### Purpose: implement decision tree with two selection strategies:
1. Information Gain Heuristic
2. Variance Impurity Heuristic

### Instructions:
- The BinaryDecisionTree.py program reads in 6 arguments in the following order:
	- L: 				integer (used in the post-pruning algorithm)
	- K: 				integer (used in the post-pruning algorithm)
	- training_set: 	CSV file containing training data, label column must be "Class"
	- validation_set: CSV file containing validation data, label column must be "Class"
	- test_set: 		CSV file containing test data, label column must be "Class"
	- to-print: 		{"yes", "no"}, if yes, print all trees according to format in assignment instructions
		
- The CSV file references can be direct paths or <filename> if the files are in same directory as the program
	
- To save console output into a file, append this command to program call " > <filename.ext>"

- Use case:
	- navigate to program directory, which is the same as dataset files, in terminal then execute the following command: 
		- python assignment1.py 15 15 training_set.csv validation_set.csv test_set.csv yes > report.txt
	
#### Note: 
_To run program in windows environment, please refer to this tutorial_
(https://www.pythoncentral.io/execute-python-script-file-shell/)
