### Program: TextClassification.py
### Language: Python 
- Version: 3.6.5
- Libraries: os.walk, os.path.join, collections.defaultdict, numpy, math.log, math.exp, nltk.corpus.stopwords, 
### Written by: Yours truly
### Imported classes: LogisticRegression.py, MultinominalNB.py
#### Purpose: Implement and evaluate Naive Bayes and Logistic Regression for text classification.
1. Naive Bayes Implementation, add-one smoothing, filtered stop-words.
2. Multinomial Naive Bayes Implementation, L2 regularization, varying lambda values, filtered stop-words.

### Instructions:
- Place TextClassification.py, LogisticRegression.py, and MultinominalNB.py in the same directory
	as the training set and test set. Make sure the training set folder is named "train" and
	the test set folder is named "test".
	
- The TextClassification.py is the only program that needs to be executed, and should take 
	about 20 minutes to complete. 
	
- The program will report the test accuracy of Naive Bayes 
	algorithm with and without stop words. It will also report the test accuracy of Logistic
	Regression algorithm with and without stop words. This result includes the learning rate,
	lambda value, and iterations for gradient descent. Number of iterations is set to 100,
	while the other two uses the combination of these values for each parameter: 
	learning_rates[0.01, 0.05, 0.1] and lambda_values[0.1,1,10]. With the data given, I
	learned that logistic regression performed the best when learning rate is 0.01 and
	lambda value is 1 for both with and without stop words.
	
- To save console output into a file, append this command to program call " > <filename.ext>"

- Use case:
  - navigate to program directory, which is the same as dataset files, in terminal then execute the following command:
    - python TextClassification.py > output.txt
	
#### Note: 
_To run program in windows environment, please refer to this tutorial_
(https://www.pythoncentral.io/execute-python-script-file-shell/)
