#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 01:28:11 2019

@author: Mike
"""

from MultinominalNB import NaiveBayes
from LogisticRegression import LogisticR

NB = NaiveBayes()
NB.train("train")
NB.test("test")

NBS = NaiveBayes()
NBS.train("train",sword=True)
NBS.test("test")

learning_rates=[0.01,0.05,0.1]
lambda_values=[0.1,1,10]
LR = LogisticR()
LRS = LogisticR()
for a in learning_rates:
    for b in lambda_values:
        LR.train("train",ap=a,ld=b)
        LR.test("test")
        
        LRS.train("train",ap=a,ld=b,sword=True)
        LRS.test("test")