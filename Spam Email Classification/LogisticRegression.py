#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 17:16:04 2019

Class to store all functions needed to train a MCAP Logistic Regression model

@author: Mike
"""

from os import walk
from os.path import join
from math import exp
import numpy as np
from nltk.corpus import stopwords

class LogisticR:
    
    def __init__(self):
        return
    
    def sigmoid(self,z):
        y = np.zeros(z.shape)
        a,b = z.shape
        for i in np.arange(a):
            for j in np.arange(b):
                if z[i,j] < 0:
                    y[i,j] = 1 - 1 / (1 + exp(z[i,j]))
                else:
                    y[i,j] = 1 / (1 + exp(-z[i,j]))
        return y
    
    def train(self, path,ap=0.01,ld=1,loop=100, sword=False):
        if sword:
            print("\n=========== Logistic Regression without stop words training begins ===========")
            self.stopwords = set(stopwords.words('english'))
        else:
            print("\n=========== Logistic Regression training begins ===========")
        print("Learning rate:", str(ap), ", Lambda value:",str(ld), ", Iterations:",str(loop))
        classes = []
        dataFiles = []
        for (root,dirs,files) in walk(path):
            classes.extend(dirs)
            for name in files:
                if not name.startswith('.'):
                    dataFiles.append(join(root,name))
        self.W, self.V, self.Ckey = self.TrainLR(classes,dataFiles,ap,ld,loop,sword)
        self.ap = ap
        self.ld = ld
        self.loop = loop
        self.sword = sword
        
    def test(self, path):
        classes = []
        dataFiles = []
        for (root,dirs,files) in walk(path):
            classes.extend(dirs)
            for name in files:
                if not name.startswith('.'):
                    dataFiles.append(join(root,name))
        N = len(dataFiles)
        #label = np.zeros((N,1))
        eCount = 0
        #predict = np.zeros((N,1))
        #print("Testing...")
        for index, d in enumerate(dataFiles):
            #label[index,0]=self.Ckey[self.getClass(classes,d)]
            dwords = self.getWordsInFile(d,self.sword)
            xInit = self.countWordsInFile(dwords,self.V)
            xIndex = np.append(np.ones((1,1)),xInit,axis=1)
            pIndex = xIndex @ self.W
            if pIndex < 0:
                # P=0
                if self.Ckey[self.getClass(classes,d)]==1:
                    eCount += 1
            else:
                # P=1
                if self.Ckey[self.getClass(classes,d)]==0:
                    eCount += 1
        if self.sword:
            print("------ Logistic Regression without stop words test result ------")
        else:
            print("------ Logistic Regression test result ------")
        print ("Correct Prediction: ", str(N - eCount),"/",str(N))
        print ("Accuracy: ", str(round((1-eCount/N)*100.0,3)),"%")
        print("\n")

                    
    def TrainLR(self,C,D,ap,ld,loop,sword):
        V = self.ExtractVocabulary(D,sword)
        N = len(D)
        W = np.random.random((len(V)+1,1))
        #Vkey = {v:index for index, v in enumerate(V)}
        Ckey = {c:index for index, c in enumerate(C)}
        label = np.zeros((N,1))
        
        #print("Preparing training data...")
        Xinit = np.zeros((N,len(V)))
        for index, d in enumerate(D):
            label[index,0]=Ckey[self.getClass(C,d)]
            dwords = self.getWordsInFile(d,sword)
            Xinit[index] = self.countWordsInFile(dwords,V)
        #print("Training data preparation complete")
        X = np.append(np.ones((N,1)),Xinit,axis=1)
        #print("Training model...")
        for a in np.arange(loop):
            predict = self.sigmoid(X @ W)
            #cost = np.sum((label-predict)**2) + ld*sum(W**2)
            dw = X.transpose() @ (label-predict)
            W = W + ap*(dw-ld*W)
            #print(cost)
        #print("Model training complete")
        return W, V, Ckey
        
    def ExtractVocabulary(self,D,sword):
        vocab = set()
        for file in D:
            vocab.update(self.getWordsInFile(file,sword))
        return vocab
    
    def getClass(self,C,d):
        for c in C:
            if c in d:
                return c
            
    def getWordsInFile(self,file,sword):
        f = open(file,"r",encoding="utf-8",errors="replace")
        words = f.read().split()
        f.close
        if sword:
            words = [v for v in words if not v in self.stopwords]
        return words
    
    def countWordsInFile(self,words,V):
        x = np.zeros((1,len(V)))
        for col,t in enumerate(V):
            x[0,col] = words.count(t)
        return x