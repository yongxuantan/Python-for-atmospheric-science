#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:17:24 2019

@author: Mike
"""

import sys
import pandas
import math
import random
import copy

# house keeping to make sure required parameters had been given
if len(sys.argv)<7 :
	print ("Missing arguments: required <L> <K> <training set file path> \
 <validation set file path> <test set file path> <to-print{yes,no}>, terminating program...")
	sys.exit()
if sys.argv[1].isdigit()==False:
    print("Invalid argument: the first argument must be a number, you gave: "+sys.argv[1])
    print("terminating program...")
    sys.exit()
if sys.argv[2].isdigit()==False:
    print("Invalid argument: the second argument must be a number, you gave: "+sys.argv[2])
    print("terminating program...")
    sys.exit()
print("Assignment1.py program output: \n")
print("Should I print all trees? {yes, no} : " + sys.argv[6])

def decision(L, K, trset, vset, tsset, p):
    
    # load datasets, return dataframe, use row 0 as column names
    trainset = pandas.read_csv(trset,header=0)
    validset = pandas.read_csv(vset,header=0)
    testset = pandas.read_csv(tsset,header=0)
    
    # check dataset sizes
    print(" ")
    print("Given training set size: " + str(trainset.shape))
    print("Given validation set size: " + str(validset.shape))
    print("Given test set size: " + str(testset.shape))
    
    # get list of attributes, excluding label column
    attrList = trainset.columns[trainset.columns!='Class']
    
    print("\nBuilding tree using Information Gain (IG) algorithm...")
    treeIG = id3(trainset,'Class',attrList,"IG")
    print("Test IG tree accuracy on test set: "+str(round(accuracy(treeIG,testset),3))+"%")
    
    print("\nPost-Pruning IG tree...")
    ptreeIG = postPrune(L, K, trainset, validset, "IG")
    print("Test Post-Pruned IG tree accuracy on validation set: "+str(round(accuracy(ptreeIG,validset),3))+"%")
    print("Test Post-Pruned IG tree accuracy on test set: "+str(round(accuracy(ptreeIG,testset),3))+"%")
    
    print("\nBuilding tree using Variance Impurity (VI) algorithm...")
    treeVI = id3(trainset,'Class',attrList,"IG")
    print("Test IG tree accuracy on test set: "+str(round(accuracy(treeVI,testset),3))+"%")

    print("\nPost-Pruning VI tree...")
    ptreeVI = postPrune(L, K, trainset, validset, "VI")
    print("Test Post-Pruned VI tree accuracy on validation set: "+str(round(accuracy(ptreeVI,validset),3))+"%")
    print("Test Post-Pruned VI tree accuracy on test set: "+str(round(accuracy(ptreeVI,testset),3))+"%")
    
    if p=="yes":
        print("\n----------- Information Gain Tree ----------")
        treeIG.print(0)
        print("\n----------- Post-Pruning Information Gain Tree ----------")
        ptreeIG.print(0)
        print("\n----------- Variance Impurity Tree ----------")
        treeVI.print(0)
        print("\n----------- Post-Pruning Variance Impurity Tree ----------")
        ptreeVI.print(0)
    
    print("\nProgram end")

def postPrune(L, K, example, valid, vType):
    # algorithm from assignment instruction sheet
    attrList = example.columns[example.columns!='Class']
    print("   Rebuilding "+str(vType)+" tree...")
    d = id3(example,'Class',attrList,vType)
    dBest = d
    vldBest = accuracy(dBest, valid)
    for i in range(0,L):
        dPrime = copy.deepcopy(d)
        m = random.randint(1,K)
        for j in range(0,m):
            nList = nonLeaf(dPrime)
            N = len(nList)
            if N>0:
                p = random.randint(0,N-1)
                chgLeaf(nList[p])
        vlPrime = accuracy(dPrime, valid)
        if vlPrime>vldBest:
            dBest=dPrime
            vldBest=vlPrime
    return dBest

def id3(example, target, attrList,vType):
    # algorithm from Tom Mitchell, page 56
    root = Node()
    if checkAll(example["Class"],1):
        root.label=1
        root.count=len(example.index)
    elif checkAll(example["Class"],0):
        root.label=0
        root.count=len(example.index)
    elif len(attrList)<=0:
        root.label=round((sum(example["Class"]))/len(example.index))
        root.count=len(example.index)
    else:
        root.leaf="No"
        A = bestGain(example,attrList,vType)
        root.attr=A
        for s in [0,1]:
            sample = example[example[A]==s]
            if sample.empty:
                eNode = Node()
                eNode.attr=A
                eNode.count=0
                eNode.label=round((sum(example["Class"]))/len(example.index))
                root.setNext(eNode,s)
            else:
                nNode=id3(sample, A, attrList[attrList != A],vType)
                nNode.count=len(sample.index)
                root.setNext(nNode,s)
    return root

def bestGain(S,L,vType):
    # return the attribute with the best gain value
    best = [L[0],0.000]
    for c in L:
        thisA=gain(S['Class'],S[c],vType)
        if thisA > best[1]:
            best[0]=c
            best[1]=thisA
    return best[0]

def gain(S,A,vType):
    # return the gain value of an attribute
    t = S.count()
    if t==0:
        return 0.000
    p = A==1
    n = A==0
    if S[p].count()==0 or S[n].count()==0:
        return 0.000
    if vType=="IG":
        sp = entropy(S[p])
        sn = entropy(S[n])
        e = entropy(S)
    elif vType=="VI":
        sp = variance(S[p])
        sn = variance(S[n])
        e = variance(S)
    else:
        print("Warning: Unrecognize vType value: "+str(vType))
        return 0.000
    gain = e - ( (A[p].count()/t)*sp + (A[n].count()/t)*sn )
    return gain

def entropy(y):
    Pplus = sum(y==1)/y.count()
    Pminus = sum(y==0)/y.count()
    if Pplus==0:
        first=0
    else:
        first= -1 * Pplus * math.log(Pplus,2)
    if Pminus==0:
        second=0
    else:
        second= -1 * Pminus * math.log(Pminus,2)
    return first + second

def variance(y):
    k = y.count()
    if k==0:
        return 0.000
    k0 = y[y==0].count()
    k1 = y[y==1].count()
    v = k0 * k1 / (k)**2
    return v

def nonLeaf(tree):
    # get all none leaf nodes in a tree
    nlist=[]
    schild=[]
    schild.append(tree)
    while(len(schild)>0):
        thisNode = schild.pop(0)
        if thisNode.leaf=="No":
            nlist.append(thisNode)
            schild.append(thisNode.leftNode)
            schild.append(thisNode.rightNode)
    return nlist

def chgLeaf(node):
    # change the given node to a leaf node
    chgNode = node
    schild=[]
    schild.append(chgNode)
    negCt=0
    posCt=0
    # loop through all leaf nodes to get positive and negative sample counts
    while(len(schild)>0):
        thisNode = schild.pop(0)
        if thisNode.leaf=="No":
            schild.append(thisNode.leftNode)
            schild.append(thisNode.rightNode)
        elif thisNode.leaf=="Yes":
            if thisNode.label==0:
                negCt=negCt+thisNode.count
            elif thisNode.label==1:
                posCt=posCt+thisNode.count
    totalCt = negCt + posCt
    if totalCt==0:
        print("This node has no majority, therefore set to 0 to avoid error")
        chgNode.label=0
    else:
        chgNode.label=round(posCt/totalCt)
    chgNode.count=totalCt
    chgNode.leaf="Yes"
    return chgNode

def accuracy(root, testset):
    # set m to sample size
    m = testset.shape[0]
    # set key to correct label
    key = testset["Class"]
    # guess is used to store list of predictions
    guess = []
    # loop throw all samples
    for r in range(0,m):
        thisrow = testset.iloc[r]
        pointer=root
        # loop throw all attributes, but it will likely break before going through all of them
        for c in range(0,thisrow.shape[0]-1):
            thisval = thisrow[pointer.attr]
            if thisval==0:
                if pointer.leftNode.leaf=="Yes":
                    guess.append(pointer.leftNode.label)
                    break
                else:
                    pointer = pointer.leftNode
            else:
                if pointer.rightNode.leaf=="Yes":
                    guess.append(pointer.rightNode.label)
                    break
                else:
                    pointer = pointer.rightNode
    
    if len(guess)!=m:
        print("Warning: Incomplete guess count. Guessed "+str(len(guess))+" out of "+str(m))
    
    # calculate the total number of incorrect guesses by adding the square of each difference
    errorsum = 0
    for row in range(0,m):
        errorsum = errorsum + (guess[row]-key[row]) ** 2
    # percent of correct equals 1 minus percent of incorrect
    percent = (1.0 - errorsum/m) * 100.0
    return percent

def checkAll(col, val):
    # if all values in a column equal to value then return true, else false
    for c in col:
        if c != val:
            return False
    return True

class Node:
    def __init__(self):
        self.attr = ""
        self.leftNode = None
        self.rightNode = None
        self.label=None
        self.leaf="Yes"
        self.count=0
    
    def setNext(self,n,s):
        if s==0:
            self.leftNode=n
        elif s==1:
            self.rightNode=n 
    
    def printLeft(self, c):
        self.leftNode.print(c)
        
    def printRight(self, c):
        self.rightNode.print(c)
    
    def print(self,c):
        if self.leftNode.leaf=="Yes":
            print("|  "*c+self.attr+" = 0 : "+str(self.leftNode.count))
        else:
            print("|  "*c+self.attr+" = 0 :")
            self.printLeft(c+1)
        if self.rightNode.leaf=="Yes":
            print("|  "*c+self.attr+" = 1 : "+str(self.rightNode.count))
        else:
            print("|  "*c+self.attr+" = 1 :")
            self.printRight(c+1)

decision(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])