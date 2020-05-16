#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 15:28:09 2019

Class to store all functions needed to train a multinominal Naive Bayes model

@author: Mike
"""

from os import walk
from os.path import join
from collections import defaultdict
from math import log
from nltk.corpus import stopwords

class NaiveBayes:
    
    def __init__(self):
        return
    
    def train(self, path, sword=False):
        if sword:
            print("\n=========== Naive Bayes without stop words training begins ===========")
            self.stopwords = set(stopwords.words('english'))
        else:
            print("\n=========== Naive Bayes training begins ===========")
        classes = []
        dataFiles = []
        for (root,dirs,files) in walk(path):
            classes.extend(dirs)
            for name in files:
                if not name.startswith('.'):
                    dataFiles.append(join(root,name))
        #print("Training model...")
        self.V, self.prior, self.condprob = self.TrainMultiNominalNB(classes,dataFiles,sword)
        #print("Training model complete!")
        self.sword = sword
    
    def test(self, path):
        #print("Testing...")
        classes = []
        dataFiles = []
        for (root,dirs,files) in walk(path):
            classes.extend(dirs)
            for name in files:
                if not name.startswith('.'):
                    dataFiles.append(join(root,name))
        
        label = {}
        predict = {}
        for c in classes:
            label[c] = self.CountDocsInClass(dataFiles, c)
            predict[c] = 0
        for d in dataFiles:
            result = self.ApplyMultiNominalNB(classes,self.V,self.prior,self.condprob,d)
            predict[result] += 1
        #error = sum([abs(label[c]-predict[c]) for c in classes])
        error = abs(label[classes[0]]-predict[classes[0]])
        if self.sword:
            print("------ Naive Bayes without stop words test result ------")
        else:
            print("------ Naive Bayes test result ------")
        print ("Correct Prediction: ", str(len(dataFiles)-error),"/",str(len(dataFiles)))
        print ("Accuracy: ", str(round((1-error/len(dataFiles))*100.0,3)),"%")
        print("\n")

    def TrainMultiNominalNB(self,C,D,sword):
        V = self.ExtractVocabulary(D,sword)
        N = self.CountDocs(D)
        prior = {}
        condprob = defaultdict(lambda:{x:1/len(V) for x in C})
        for c in C:
            Nc = self.CountDocsInClass(D, c)
            prior[c] = Nc/N
            textc = self.ConcatenateTextOfAllDocsInClass(D,c,sword)
            for t in V:
                Tct = self.CountTokensOfTerm(textc,t)
                condprob[t][c] = (Tct + 1)/(len(textc)+len(V))
        return V, prior, condprob
    
    def ExtractVocabulary(self,D,sword):
        vocab = set()
        for file in D:
            f = open(file,"r",encoding="utf-8",errors="replace")
            words = f.read().split()
            vocab.update(words)
            f.close
        if sword:
            vocab = set([v for v in vocab if not v in self.stopwords])
        return vocab
    
    def CountDocs(self,D):
        return len(D)
    
    def CountDocsInClass(self,D,c):
        matching = [s for s in D if c in s]
        return len(matching)
    
    def ConcatenateTextOfAllDocsInClass(self,D,c,sword):
        vocabC = []
        matching = [s for s in D if c in s]
        for file in matching:
            f = open(file,"r",encoding="utf-8",errors="replace")
            words = f.read().split()
            vocabC.extend(words)
            f.close
        if sword:
            vocabC = [v for v in vocabC if not v in self.stopwords]
        return vocabC
    
    def CountTokensOfTerm(self,textc,t):
        return textc.count(t)
    
    def ApplyMultiNominalNB(self,C,V,prior,condprob,d):
        W = self.ExtractTokensFromDoc(V,d)
        score = {}
        for c in C:
            score[c] = log(prior[c])
            for t in W:
                score[c] += log(condprob[t][c])
        return max(score, key=score.get)
        
    def ExtractTokensFromDoc(self,V,d):
        f = open(d,"r",encoding="utf-8",errors="replace")
        words = f.read().split()
        f.close
        return V.intersection(set(words))