#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Apr 14

@author: Yongxuan Tan
"""

import os
import numpy
import pandas as pd
import random
import copy
import sys

# house keeping to make sure required parameters had been given
if len(sys.argv)<1 :
	print ("Missing arguments: required <UAI-file> <task-id> <training-data> <test-data>, terminating program...")
	sys.exit()
if os.path.isfile(sys.argv[1])==False:
    print("The UAI file is invalid or not exist.")
    print("terminating program...")
    sys.exit()
if os.path.isfile(sys.argv[3])==False:
    print("The training data file is invalid or not exist.")
    print("terminating program...")
    sys.exit()
if os.path.isfile(sys.argv[4])==False:
    print("The test data file is invalid or not exist.")
    print("terminating program...")
    sys.exit()
print("Structural-Learning.py program output: \n")

# set variables
input_uai_file = sys.argv[1]
task_id = int(sys.argv[2])
training_data = sys.argv[3]
test_data = sys.argv[4]
eps = 0.00001


"""Declare Variable and Clique function classes"""

class variable:
  def __init__(self,id,d):
    self.id = id
    self.d = d

  def setClique(self,c):
    self.clique = c
  
  def setParent(self,p):
    self.parents = p

  def __repr__(self):
    return "\n<id:" + self.id + " size:" + str(self.d) + ">"

class clique:
  def __init__(self, d):
    self.variables = []
    self.num = d
    self.cpd = 0
    self.dot_func = []

  def addVar(self, v):
    self.variables.append(v)
  
  def addFunc(self, f):
    self.dot_func.append(f)

  def setCPD(self, c):
    self.cpd = c

  def contain(self, i):
    for x in range(0,self.num):
      thisVar = self.variables[x]
      if thisVar.id == i:
        return True
    return False

  def toDF(self):
    names = []
    for v in self.variables:
      names.append(v.id)
    d = { names[i] : range(self.cpd) for i in range(self.num)}
    d2 = pd.DataFrame(d)
    d2['value'] = self.dot_func
    for n in range(self.num):
      t1 = d2[names[n]] / self.cpd * (2 ** n) + 0.0000001
      d2[names[n]] = round(t1 % 1)
    self.df = d2

  def reduce(self, i, a):
    for x in range(self.num):
      thisVar = self.variables[x]
      if thisVar.id == i:
        aFloat = float(a)
        tempDF = self.df
        tempDF.loc[(tempDF[i] != aFloat),'value']=0.0
        tempDF.drop(tempDF[tempDF['value'] == 0.0].index, inplace=True)
        self.df = tempDF
        self.cpd = tempDF.shape[0]
        self.dot_func = tempDF['value'].tolist()
        return True
    return False

  def __repr__(self):
    line = "\n<Clique size:" + str(self.num) + " vars:"
    for x in range(0,self.num):
      thisVar = self.variables[x]
      line += thisVar.id + ","
    line += " cpd size:" + str(self.cpd) + " cpd:"
    for x in range(0,self.cpd):
      line += str(self.dot_func[x]) + ","
    return line + ">"

def loadMLE(training_data):
  f = open(training_data)

  line = f.readline()
  linelist = line.split()      # split line into list by space

  numVar = int(linelist[0])
  numData = int(linelist[1])

  ds = []

  for m in range(numData):      # loop through all data lines

    line = f.readline()
    linelist = line.split()      # split line into list by space

    ds.append([int(l) for l in linelist])    # add row to dataset
  # finish reading file

  # convert dataset to dataframe format
  dataset = pd.DataFrame(ds, columns=[str(n) for n in range(numVar)])
  return dataset

def trainMLE(task, varList, dataset, eps):
  for v in varList:
    if len(v.parents) == 0:
      ds = []
      for d in range(v.d):
        pr = sum(dataset[v.id]==d) / dataset.shape[0]
        if pr == 0.0:
          pr = eps
        ds.append(pr)
      sSum = sum(ds)
      v.clique.df[task] = numpy.divide(ds,sSum)
    else:
      parent = [p.id for p in v.parents]
      top = parent.copy()
      top.append(v.id)
      tmpDF = v.clique.df[top]
      tmpDS1 = dataset[parent].groupby(parent,as_index=False).size().reset_index(name='pBot')
      tmpDS2 = dataset[top].groupby(top,as_index=False).size().reset_index(name='pTop')
      tmpDS3 = pd.merge(tmpDS2,tmpDS1,on=parent)
      tmpDS3[task] = tmpDS3["pTop"] / tmpDS3["pBot"]
      tmpDF = tmpDF.merge(tmpDS3.drop(columns=['pTop','pBot']),how='left',on=top).fillna(eps)
      sSum = tmpDF[task].sum()
      v.clique.df[task] = tmpDF[task] / sSum
  return varList

def loadTestData(test_data):
  f = open(test_data)

  line = f.readline()
  linelist = line.split()      # split line into list by space
  numTestVar = int(linelist[0])
  numTestData = int(linelist[1])

  testDS = []

  for m in range(numTestData):      # loop through all data lines
    line = f.readline()
    linelist = line.split()      # split line into list by space

    testDS.append([int(l) for l in linelist])    # add row to dataset
  # finish reading file

  # convert dataset to dataframe format
  testData = pd.DataFrame(testDS, columns=[str(n) for n in range(numTestVar)])
  return testData

def test(task, testData, varList):
  testData["LLo"] = numpy.zeros(testData.shape[0])
  testData["LLl"] = numpy.zeros(testData.shape[0])
  for v in varList:
    if len(v.parents) == 0:
      tmpV = v.clique.df
      tmpV1 = testData.merge(tmpV,how='left',on=[v.id])
      testData["LLo"] = testData["LLo"] + tmpV1["value"].apply(numpy.log)
      testData["LLl"] = testData["LLl"] + tmpV1[task].apply(numpy.log)
    else:
      tmpV = v.clique.df
      top = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
      tmpV1 = testData.merge(tmpV,how='left',on=top)
      testData["LLo"] = testData["LLo"] + tmpV1["value"].apply(numpy.log)
      testData["LLl"] = testData["LLl"] + tmpV1[task].apply(numpy.log)

  testData["LLDiff"] = testData["LLo"] - testData["LLl"]
  testData["LLDiff"] = testData["LLDiff"].apply(numpy.abs)

  LLDiffSum = testData["LLDiff"].sum()
  return LLDiffSum

def buildMLE(task, training_data, test_data, varList, eps):
  dataset = loadMLE(training_data)
  varList = trainMLE(task, varList, dataset, eps)
  testData = loadTestData(test_data)
  LLDiffSum = test(task, testData, varList)
  print(" ************  Result for task: "+task+": *************** ")
  print("log likelihood difference = " + str(LLDiffSum))
  print("Trainig data from: "+training_data)
  print("Test data from: "+test_data)
  return True

def initializeEM(task, varList, eps):
  for v in varList:
    if len(v.parents) == 0:
      pr = random.random()
      if pr == 0.0:
        pr = eps
      v.clique.df[task] = [pr,1-pr]
    else:
      ds = []
      for x in range(2**len(v.parents)):
        pr = random.random()
        if pr == 0.0:
          pr = eps
        ds.extend([pr,1-pr])
      v.clique.df[task] = ds
  return varList

def loadEM(task, training_data, varList):
  f = open(training_data)

  line = f.readline()
  linelist = line.split()      # split line into list by space
  numVar = int(linelist[0])
  numData = int(linelist[1])

  colAll = [str(n) for n in range(numVar)]
  colAll.insert(0,"prob")
  colAll.append("weight")
  allDS = pd.DataFrame(columns = colAll)

  for m in range(numData):      # loop through all data lines
    rowDF = pd.DataFrame([1],columns=["prob"])
    qVar = []
    line = f.readline()
    linelist = line.split()      # split line into list by space

    for n in range(numVar):     # loop through all variable values   
      nVar = linelist[n]   
      if nVar == "?":
        tVar = varList[n]
        qVar.append(tVar)
        DF0 = rowDF.copy()
        DF1 = rowDF.copy()
        DF0[str(n)] = [0] * DF0.shape[0]
        DF1[str(n)] = [1] * DF1.shape[0]
        rowDF = pd.concat([DF0,DF1])
      else:
        rowDF[str(n)] = [int(nVar)] * rowDF.shape[0]
    rowDF.reset_index(drop=True,inplace=True)
    for i in qVar:
      tmpV = i.clique.df
      cols = [t for t in tmpV.columns if t != "MLE" and t != "value"]
      merOn = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
      tmpV1 = rowDF.merge(tmpV[cols],how='left',on=merOn)
      rowDF["prob"] = rowDF["prob"] * tmpV1[task]
    rowSum = rowDF["prob"].sum()
    rowDF["weight"] = rowDF["prob"] / rowSum
    allDS = pd.concat([allDS,rowDF])

  allDS.reset_index(drop=True,inplace=True)
  # finish reading file
  return allDS

def trainEM(task, varList, allDS, eps):
  for v in varList:
    if len(v.parents) == 0:
      ds = []
      for d in range(v.d):
        pr = sum(allDS[v.id]==d) / allDS.shape[0]
        if pr == 0.0:
          pr = eps
        ds.append(pr)
      sSum = sum(ds)
      v.clique.df[task] = numpy.divide(ds,sSum)
    else:
      parent = [p.id for p in v.parents]
      top = parent.copy()
      top.append(v.id)
      tmpDF = v.clique.df[top]
      tmpDS1 = allDS[parent].groupby(parent,as_index=False).size().reset_index(name='pBot')
      tmpDS2 = allDS[top].groupby(top,as_index=False).size().reset_index(name='pTop')
      tmpDS3 = pd.merge(tmpDS2,tmpDS1,on=parent)
      tmpDS3[task] = tmpDS3["pTop"] / tmpDS3["pBot"]
      tmpDF = tmpDF.merge(tmpDS3.drop(columns=['pTop','pBot']),how='left',on=top).fillna(eps)
      sSum = tmpDF[task].sum()
      v.clique.df[task] = tmpDF[task] / sSum
  return varList

def buildEM(task, training_data, test_data, varList, eps):
  for w in range(5):
    varList = initializeEM(task, varList, eps)
    dataset = loadEM(task, training_data, varList)
    for z in range(20):
      #print("Running EM iteration: "+str(z))
      varList = trainEM(task, varList, dataset, eps)
    testData = loadTestData(test_data)
    LLDiffSum = test(task, testData, varList)
    print(" ************  Result for task: "+task+", randomization: "+str(w)+": *************** ")
    print("log likelihood difference = " + str(LLDiffSum))
    print("Trainig data from: "+training_data)
    print("Test data from: "+test_data)
  return True



def addEdge(permu):
  for i in range(1,len(permu)):
    v = permu[i]
    r = random.randint(0,3)
    if i > r:
      v.parents = random.sample(permu[0:i-1],r)
    else:
      v.parents = permu[0:i-1]

def initDAGWeight(task, newvl):
  for v in newvl:
    v.clique.variables=[]
    v.clique.variables.append(v)
    if len(v.parents) == 0:
      pr = random.random()
      if pr == 0.0:
        pr = eps
      d = {v.id:[0,1], task:[pr,1-pr]}
      v.clique.df = pd.DataFrame(data=d)
      v.clique.num = 1
    else:
      names = []
      val = []
      v.clique.variables.extend(v.parents)
      for p in v.parents:
        names.append(p.id)
      names.append(v.id)
      v.clique.num = len(names)
      d = { names[i] : range(2 ** len(names)) for i in range(len(names))}
      for j in range(2 ** (len(names)-1)):
        pr = random.random()
        if pr == 0.0:
          pr = eps
        val.append(pr)
        val.append(1-pr)
      d2 = pd.DataFrame(d)
      d2[task] = val
      for n in range(len(names)):
        t1 = d2[names[n]] / d2.shape[0] * (2 ** n) + 0.0000001
        d2[names[n]] = round(t1 % 1)
      v.clique.df = d2
    v.clique.cpd = v.clique.df.shape[0]
    v.clique.dot_func = v.clique.df[task]
  return newvl

def initLatent(task, k, varList):
  vk = variable(str(len(varList)),k)
  vk.setClique(clique(k))
  vk.clique.variables=[]
  vk.clique.variables.append(vk)
  prb = []
  for i in range(k):
    pr = random.random()
    if pr == 0.0:
      pr = eps
    prb.append(pr)
  prb = numpy.divide(prb,sum(prb))
  d = {vk.id:range(k), task:prb}
  vk.clique.df = pd.DataFrame(data=d)
  vk.clique.num = 1
  vk.clique.cpd = vk.clique.df.shape[0]
  vk.clique.dot_func = vk.clique.df[task]
  vk.setParent([])
  return vk

def loadMRB(task, training_data, vl1, vk):
  f = open(training_data)

  line = f.readline()
  linelist = line.split()      # split line into list by space
  numVar = int(linelist[0])
  numData = int(linelist[1])

  colAll = [str(n) for n in range(numVar)]
  colAll.append(vk.id)
  colAll.insert(0,"prob")
  colAll.append("weight")
  allDS = pd.DataFrame(columns = colAll)

  for m in range(numData):      # loop through all data lines

    rowDF = pd.DataFrame([1],columns=["prob"])
    qVar = []

    line = f.readline()
    linelist = line.split()      # split line into list by space
    linelist.append('?')

    for n in range(numVar+1):     # loop through all variable values   
      nVar = linelist[n]   
      if nVar == "?":
        tVar = vl1[n]
        qVar.append(tVar)
        DF0 = rowDF.copy()
        DF1 = rowDF.copy()
        DF0[str(n)] = [0] * DF0.shape[0]
        DF1[str(n)] = [1] * DF1.shape[0]
        rowDF = pd.concat([DF0,DF1])
      else:
        rowDF[str(n)] = [int(nVar)] * rowDF.shape[0]
    rowDF.reset_index(drop=True,inplace=True)
    for i in qVar:
      tmpV = i.clique.df
      cols = [t for t in tmpV.columns if t != "MLE" and t != "value"]
      merOn = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
      tmpV1 = rowDF.merge(tmpV[cols],how='left',on=merOn)
      rowDF["prob"] = rowDF["prob"] * tmpV1[task]
    rowSum = rowDF["prob"].sum()
    rowDF["weight"] = rowDF["prob"] / rowSum
    allDS = pd.concat([allDS,rowDF])

  allDS.reset_index(drop=True,inplace=True)
  #print(allDS)
  return allDS

def getMRBweight(task, training_data, varList):
  f = open(training_data)

  line = f.readline()
  linelist = line.split()      # split line into list by space

  numVar = int(linelist[0])
  numData = int(linelist[1])

  ds = []

  for m in range(numData):      # loop through all data lines

    line = f.readline()
    linelist = line.split()      # split line into list by space

    ds.append([int(l) for l in linelist])    # add row to dataset
  # finish reading file

  # convert dataset to dataframe format
  testData = pd.DataFrame(ds, columns=[str(n) for n in range(numVar)])

  # ------------------------------------------------------------------
  testData["LLl"] = numpy.zeros(testData.shape[0])
  for v in varList:
    if len(v.parents) == 0:
      tmpV = v.clique.df
      tmpV1 = testData.merge(tmpV,how='left',on=[v.id])
      testData["LLl"] = testData["LLl"] + tmpV1[task].apply(numpy.log)
    else:
      tmpV = v.clique.df
      top = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
      tmpV1 = testData.merge(tmpV,how='left',on=top)
      testData["LLl"] = testData["LLl"] + tmpV1[task].apply(numpy.log)

  LLDiffSum = testData["LLl"].apply(numpy.abs).sum()
  return LLDiffSum

def testMRB(task, testData, varList, dag, vk):
  testData["LLo"] = numpy.zeros(testData.shape[0])
  testData["LLl"] = numpy.zeros(testData.shape[0])
  #for v in varList:
  for i in range(len(varList)):
    v=varList[i]
    tmpV = v.clique.df
    top = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
    tmpV1 = testData.merge(tmpV,how='left',on=top)
    testData["LLo"] = testData["LLo"] + tmpV1["value"].apply(numpy.log)
    for j in range(vk.d):
      vx = dag[j][i]
      prbx = vk.clique.df[task][j]
      tmpV = vx.clique.df
      top = [t for t in tmpV.columns if t != "MLE" and t != "value" and t != "EM"]
      tmpV1 = testData.merge(tmpV,how='left',on=top)
      testData["LLl"] = testData["LLl"] + prbx*tmpV1[task].apply(numpy.log)

  testData["LLDiff"] = testData["LLo"] - testData["LLl"]
  testData["LLDiff"] = testData["LLDiff"].apply(numpy.abs)

  LLDiffSum = testData["LLDiff"].sum()
  return LLDiffSum

def buildMRB(k, task, training_data, test_data, varList, eps):
  for w in range(5):
    dag = []
    vk = initLatent(task, k, varList)

    for i in range(k):
      newvl = copy.deepcopy(varList)
      permu = random.sample(newvl,len(newvl))
      for v in permu:
        v.parents=[]
      addEdge(permu)
      newvl = initDAGWeight(task, newvl)
      dag.append(newvl)
  
    for z in range(1):
      #print("Running EM iteration: "+str(z))
      probCount = []
      for i in range(k):
        vl = dag[i].copy()
        vl.append(vk)
        dataset = loadMRB(task, training_data, vl, vk)
        dag[i] = trainEM(task, dag[i], dataset, eps)
        prob = getMRBweight(task, training_data, dag[i])
        if prob == 0.0:
          prob = eps
        probCount.append(prob)
    
      pSum = sum(probCount)
      vk.clique.df[task] = numpy.divide(probCount, pSum)

    testData = loadTestData(test_data)
    LLDiffSum = testMRB(task, testData, varList, dag, vk)
    print(" ************  Result for task: Mixture-Random-bayes, k: "+str(k)+": *************** ")
    print(" ************  randomization: "+str(w)+": *************** ")
    print("log likelihood difference = " + str(LLDiffSum))
    print("Trainig data from: "+training_data)
    print("Test data from: "+test_data)

  return True

# create helper variable to aimed UAI extraction
isValidInput = False
isNumVar = False
isNumClique = False
isVarLine = False
isCliqueLine = False
isCliqueProb = False
numVar = 0
numClique = 0

Z = 0

# create two list to store Variables and Clique functions
varList = []
cliqueList = []

"""Load UAI file"""

f = open(input_uai_file)
stream = (x for x in f.read().split()) 

varCount = 0   
cliqueCount = 0  
item = next(stream)

if item == "BAYES":
  print("BAYES network implementing...")
  item = next(stream)
  varCount = int(item)

  for i in range(varCount):
    item = next(stream)
    varList.append(variable(str(i),int(item)))

  item = next(stream)
  cliqueCount = int(item)

  for c in range(cliqueCount):
    # create new clique based on information from this line
    item = next(stream)
    thisCliqueSize = int(item)
    thisClique = clique(thisCliqueSize)

    for x in range(thisCliqueSize):
      item = next(stream)
      tVar = varList[int(item)]       # keep track of who this clique belong to
      thisClique.addVar(tVar)

    # add clique to list
    cliqueList.append(thisClique)
    # assign clique to last variable
    tVar.setClique(thisClique)
    tVar.setParent([p for p in thisClique.variables if p != tVar])       

  for d in cliqueList:     
    item = next(stream)
    thisClique = d
    thisClique.setCPD(int(item))

    for y in range(thisClique.cpd):
      item = next(stream)
      thisClique.addFunc(float(item))
# finish reading UAI file

# convert clique functions into dataframe
for x in cliqueList:
  x.toDF()

if task_id == 1:
  task = "MLE"
  buildMLE(task, training_data, test_data, varList, eps)
elif task_id == 2:
  task = "EM"
  buildEM(task, training_data, test_data, varList, eps)
elif task_id == 3:
  task = "EM"
  buildMRB(2, task, training_data, test_data, varList, eps)
  buildMRB(4, task, training_data, test_data, varList, eps)
  buildMRB(6, task, training_data, test_data, varList, eps)

