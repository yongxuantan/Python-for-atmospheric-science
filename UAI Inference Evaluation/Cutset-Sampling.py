#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mar 14

@author: Yongxuan Tan
"""

import os
import numpy
import pandas as pd
from functools import reduce
import random
import math
import time
import sys

# house keeping to make sure required parameters had been given
if len(sys.argv)<1 :
	print ("Missing arguments: required <UAI file directory> <evidence file path>, terminating program...")
	sys.exit()
if os.path.isdir(sys.argv[1])==False:
    print("The UAI file directory you provided is invalid or not exist.")
    print("terminating program...")
    sys.exit()
print("Cutset-Sampling.py program output: \n")

"""Declare Variable and Clique function classes"""

class variable:
  def __init__(self,id,d):
    self.id = id
    self.d = d

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
    self.dot_func.append(numpy.log(f))

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
        tempDF.loc[(tempDF[i] != aFloat),'value']=-1.0
        tempDF.drop(tempDF[tempDF['value'] == -1.0].index, inplace=True)
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

fList=[[sys.argv[1]+"/Grids_14.uai",sys.argv[1]+"/Grids_14.uai.evid",sys.argv[1]+"/Grids_14.uai.PR"]
      ,[sys.argv[1]+"/Grids_15.uai",sys.argv[1]+"/Grids_15.uai.evid",sys.argv[1]+"/Grids_15.uai.PR"]
      ,[sys.argv[1]+"/Grids_16.uai",sys.argv[1]+"/Grids_16.uai.evid",sys.argv[1]+"/Grids_16.uai.PR"]
      ,[sys.argv[1]+"/Grids_17.uai",sys.argv[1]+"/Grids_17.uai.evid",sys.argv[1]+"/Grids_17.uai.PR"]
      ,[sys.argv[1]+"/Grids_18.uai",sys.argv[1]+"/Grids_18.uai.evid",sys.argv[1]+"/Grids_18.uai.PR"]
       ]
wList=[1,2,3,4,5]
nList=[100,1000,10000,20000]
rSeed = [10,20,30,40,50,60,70,80,90,100]

def loadUAI(fUAI,fEvid,fPR):
  # create helper variable to aid UAI extraction
  isValidInput = False
  isNumVar = False
  isNumClique = False
  isVarLine = False
  isCliqueLine = False
  isCliqueProb = False
  numVar = 0
  numClique = 0

  # create two list to store Variables and Clique functions
  varList = []
  cliqueList = []

  # -------- Load UAI file  --------
  f = open(fUAI)
  line = f.readline()
  lineCount = 0     # use to find the 4th line
  cliqueLineCount = 0        # use to keep track of which clique information this line belong to
  cliqueCount = 0            # use to identify the clique information on next line
  isProbLine = False         
  cnt = 1
  while line:      # loop through all lines
    linelist = line.split()      # split line into list by space
    if len(linelist) > 0:        # skip empty lines
      if linelist[0] != "c":     # skip comment lines
        lineCount += 1
        if lineCount == 4:       # 4th valid line is the number of cliques
          isNumClique=True
        if linelist[0] == "MARKOV":      # indicate valid input
          print("MARKOV")
          isNumVar = True
          isValidInput = True
        elif isValidInput:              # only perform if input is valid
          if isVarLine:                 # line contain all variables, once
            isVarLine = False
            for i in range(0,numVar):
              varList.append(variable(str(i),int(linelist[i])))              # create a variable for each item in this line
          if isCliqueProb:              # process CPD, this will continue to end of document
            if cliqueCount < numClique:
              if isProbLine:             # line with CPD
                thisClique = cliqueList[cliqueCount]
                for y in range(0,thisClique.cpd):
                  thisClique.addFunc(float(linelist[y]))
                cliqueCount += 1
                isProbLine = False
              else:                      # line with number of CPD on next line
                thisClique = cliqueList[cliqueCount]
                thisClique.setCPD(int(linelist[0]))
                isProbLine = True
          if isCliqueLine:              # line contain clique relationship
            if cliqueLineCount < numClique:     # keep track of how many relationship have been entered
              # create new clique based on information from this line
              thisCliqueSize = int(linelist[0])
              thisClique = clique(thisCliqueSize)
              for x in range(0,thisCliqueSize):
                thisClique.addVar(varList[int(linelist[x+1])])
              # add clique to list
              cliqueList.append(thisClique)
              cliqueLineCount += 1
              if cliqueLineCount == numClique:      # finished all clique relationships
                isCliqueProb = True       # change to process probability table
                isCliqueLine = False                           
          if isNumVar:                  # extract num var value, once
            numVar = int(linelist[0])
            isNumVar = False
            isVarLine = True            # next line is variable line
          if isNumClique:               # extract num clique value, once
            numClique = int(linelist[0])
            isNumClique = False
            isCliqueLine = True
    line = f.readline()
    cnt += 1
  # finish reading UAI file
  # convert clique functions into dataframe
  for x in cliqueList:
    x.toDF()

  # ----  Load evidence file  ---------
  fevid = open(fEvid)
  line = fevid.readline()      
  linelist = line.split()      # split line into list by space
  evidVars = []
  evidIndex = 0
  numEvid = int(linelist[evidIndex])
  if numEvid > 0:              # instantiate evidence
    print(linelist)
    evidIndex += 1
    for x in range(numEvid):
      evidID = linelist[evidIndex+x]
      evidValue = linelist[evidIndex+x+1]
      evidVars.append(evidID)
      for y in cliqueList:
        out = y.reduce(evidID,evidValue)
      evidIndex += 1
  
  # ----- Load PR file  ----------
  fpr = open(fPR)
  line = fpr.readline()
  if line.split()[0]=="PR":
    line=fpr.readline()
    baseZ=float(line.split()[0])
  else:
    baseZ=0.0

  return varList, cliqueList, evidVars, baseZ

def logaddsum(series):
  return reduce(lambda x,y: numpy.logaddexp(x, y),series)

def getCutset(varList,cliqueList,evidVars,w):
  # -------- calculate cutset variable ordering  ---------
  minOrder = {}
  wMet = True                     # if w-cutset met then stop loop at the end
  for b in varList:           
    vID = b.id
    if (vID not in evidVars):     # loop through all non-evidence variables
      clqCnt = set()
      for c in cliqueList:
        if c.contain(vID):        # increase count if variable found in clique function
          for z in c.variables:
            clqCnt.add(z.id)
      if len(clqCnt) > w:
          wMet = False
      minOrder[vID] = len(clqCnt)
  # sort by max degree order for cutset 
  maxOrderSorted = sorted(minOrder.items(), key=lambda x: x[1], reverse=True)

  # ------ calculate wCutset  --------------
  X = []
  XVar = []
  tempCliqueList = cliqueList.copy()
  tempVarList = varList.copy()
  if not wMet:
    for a,b in maxOrderSorted:
      wMet = True                     # if w-cutset met then stop loop at the end
      newCliqueList = []              # store irrelevant cliques
      workingCliqueList = []          # store relevant cliques
      for h in tempCliqueList:            # loop through all cliques to find the ones we need
        if h.contain(a):
          workingCliqueList.append(h)
        else:
          newCliqueList.append(h)
      for g in workingCliqueList:
        if g.num > 1:
          myDF = g.df
          gbvar = [z.id for z in g.variables]
          gbvar.remove(a)
          newDF = myDF.groupby(gbvar,as_index=False).sum().drop(columns=[a])
          newClique = clique(len(gbvar))       # create new clique function 
          newClique.variables = [z for z in g.variables if z.id != a]
          newClique.cpd = newDF.shape[0]
          newClique.dot_func = newDF['value'].tolist()
          newClique.df = newDF
          newCliqueList.append(newClique)
      tempCliqueList = newCliqueList                 # update clique functions list to new one
      print("Variable " + a + " is removed from cutset.")
      x1 = varList[int(a)]
      tempVarList.remove(x1)
      X.append(a)
      XVar.append(x1)
      for b in tempVarList:           
        vID = b.id
        clqCnt = set()
        for c in tempCliqueList:
          if c.contain(vID):        # increase count if variable found in clique function
            for z in c.variables:
              clqCnt.add(z.id)
        if len(clqCnt) > w:
          wMet = False
      if wMet:
        print("met")
        break

  return XVar,tempCliqueList

"""calculate estZ"""

def uniformZ(N,XVar,cliqueList,varList):
  estZ = 0.0
  for i in range(N):
    print("Calculating iteration: " + str(i))
    # -------- generate sample  ---------
    Q = numpy.log(1.0)
    myEvidVar = [str(len(XVar))]
    thisEvidVar = []
    for a in XVar:
      myEvidVar.append(a.id)
      myEvidVar.append(str(math.floor(random.random()*a.d)))
      Q = Q - numpy.log(float(a.d))
      thisEvidVar.append(a.id)

    # -------- set evidence in PGM  ---------
    thisCliqueList = []
    for o in cliqueList:
        newClique = clique(len(o.variables))       # create new clique function 
        newClique.variables = [z for z in o.variables]
        newClique.cpd = o.df.shape[0]
        newClique.dot_func = o.df['value'].tolist()
        newClique.df = o.df.copy()
        thisCliqueList.append(newClique)
    linelist = myEvidVar
    evidVars = []
    evidIndex = 0
    numEvid = int(linelist[evidIndex])
    if numEvid > 0:              # instantiate evidence
      evidIndex += 1
      for x in range(numEvid):
        evidID = linelist[evidIndex+x]
        evidValue = linelist[evidIndex+x+1]
        evidVars.append(evidID)
        for y in thisCliqueList:
          out = y.reduce(evidID,evidValue)
          if y.cpd==0:
            thisCliqueList.remove(y)
        evidIndex += 1

    # calculate elimination order
    thisMinOrder = {}
    for b in varList:           
      vID = b.id
      if (vID not in thisEvidVar):     # loop through all non-evidence variables
        clqCnt = 0
        for c in thisCliqueList:
          if c.contain(vID):        # increase count if variable found in clique function
            clqCnt += 1
        thisMinOrder[vID] = clqCnt
    thisMinOrderSorted = sorted(thisMinOrder.items(), key=lambda x: x[1])
    thisMinOrderSortedList = [a for a,b in thisMinOrderSorted]
    thisMinOrderSortedList = thisMinOrderSortedList + thisEvidVar         # add evidence variables to the end

    #Run the variable elimination algorithm
    for a in thisMinOrderSortedList:
      newCliqueList = []              # store irrelevant cliques
      workingCliqueList = []          # store relevant cliques
      for h in thisCliqueList:            # loop through all cliques to find the ones we need
        if h.contain(a):
          workingCliqueList.append(h)
        else:
          newCliqueList.append(h)
      workingVars = set()             # store variables involved in this elimination cycle
      isFirstDF = True
      for g in workingCliqueList:
        for d in g.variables:
          workingVars.add(d.id)
        if isFirstDF:
          isFirstDF = False
          lastDF = g.df
        else:
          thisDF = g.df
          # find common variables between two clique tables, except factor column
          commonVar = numpy.intersect1d(lastDF.columns,thisDF.columns).tolist()
          commonVar.remove('value')
          temp1 = lastDF.merge(thisDF, left_on=commonVar, right_on=commonVar)    # merge two cliques tables into one
          temp1['value'] = temp1['value_x']+temp1['value_y']                     # add two log factors
          # sum up the new factors
          temp2 = temp1.groupby(sorted(workingVars),as_index=False).agg(logaddsum).drop(columns=['value_x','value_y'])
          lastDF = temp2
      # sum up the results around elimination variable
      sortVar = sorted([q for q in workingVars if q != a])
      if len(sortVar) == 0:                                 # no more variables, break the loop and return Z
        #print(lastDF)
        if len(lastDF['value'])==2:
          VE = numpy.logaddexp(lastDF['value'][0], lastDF['value'][1])
        else:
          VE = lastDF['value'][0]
        break
      newDF = lastDF.groupby(sortVar,as_index=False).agg(logaddsum).drop(columns=[a])
      workingVars.remove(a)                      # drop elimination variable from current clique
      newClique = clique(len(workingVars))       # create new clique function 
      for x in sorted(workingVars):
        newClique.addVar(varList[int(x)])
      newClique.cpd = newDF.shape[0]
      newClique.dot_func = newDF['value'].tolist()
      newClique.df = newDF
      newCliqueList.append(newClique)
      thisCliqueList = newCliqueList                 # update clique functions list to new one

    # weight of sample
    thisW = VE - Q
    estZ = numpy.logaddexp(estZ,thisW)
    estZ = (estZ - numpy.log(N)) / numpy.log(10)

  return estZ

def adaptiveZ(N,XVar,cliqueList,varList):
  estZ = 0.0
  sampleT = {v.id:[] for v in XVar}
  sampleT['weight']=[]
  QX = {v.id:[b/v.d for b in range(v.d)] for v in XVar}
  for i in range(N):
    print("Calculating iteration: " + str(i))
    # -------- generate sample  ---------
    Q = numpy.log(1.0)
    myEvidVar = [str(len(XVar))]
    thisEvidVar = []
    for a in XVar:
      myEvidVar.append(a.id)
      ranNum = random.random()
      tCt=0
      pChance=0.0
      for b in QX[a.id]:
        if ranNum >= b:
          tX = tCt
          pChance=1-b
        else:
          pChance=pChance-(1-b)
          break
        tCt += 1
      Q = Q + numpy.log(pChance)
      myEvidVar.append(str(tX))
      sampleT[a.id].append(tX)
      thisEvidVar.append(a.id)

    # -------- set evidence in PGM  ---------
    thisCliqueList = []
    for o in cliqueList:
        newClique = clique(len(o.variables))       # create new clique function 
        newClique.variables = [z for z in o.variables]
        newClique.cpd = o.df.shape[0]
        newClique.dot_func = o.df['value'].tolist()
        newClique.df = o.df.copy()
        thisCliqueList.append(newClique)
    linelist = myEvidVar
    evidVars = []
    evidIndex = 0
    numEvid = int(linelist[evidIndex])
    if numEvid > 0:              # instantiate evidence
      evidIndex += 1
      for x in range(numEvid):
        evidID = linelist[evidIndex+x]
        evidValue = linelist[evidIndex+x+1]
        evidVars.append(evidID)
        for y in thisCliqueList:
          out = y.reduce(evidID,evidValue)
          if y.cpd==0:
            thisCliqueList.remove(y)
        evidIndex += 1

    # calculate elimination order
    thisMinOrder = {}
    for b in varList:           
      vID = b.id
      if (vID not in thisEvidVar):     # loop through all non-evidence variables
        clqCnt = 0
        for c in thisCliqueList:
          if c.contain(vID):        # increase count if variable found in clique function
            clqCnt += 1
        thisMinOrder[vID] = clqCnt
    thisMinOrderSorted = sorted(thisMinOrder.items(), key=lambda x: x[1])
    thisMinOrderSortedList = [a for a,b in thisMinOrderSorted]
    thisMinOrderSortedList = thisMinOrderSortedList + thisEvidVar         # add evidence variables to the end

    #Run the variable elimination algorithm
    for a in thisMinOrderSortedList:
      newCliqueList = []              # store irrelevant cliques
      workingCliqueList = []          # store relevant cliques
      for h in thisCliqueList:            # loop through all cliques to find the ones we need
        if h.contain(a):
          workingCliqueList.append(h)
        else:
          newCliqueList.append(h)
      workingVars = set()             # store variables involved in this elimination cycle
      isFirstDF = True
      for g in workingCliqueList:
        for d in g.variables:
          workingVars.add(d.id)
        if isFirstDF:
          isFirstDF = False
          lastDF = g.df
        else:
          thisDF = g.df
          # find common variables between two clique tables, except factor column
          commonVar = numpy.intersect1d(lastDF.columns,thisDF.columns).tolist()
          commonVar.remove('value')
          temp1 = lastDF.merge(thisDF, left_on=commonVar, right_on=commonVar)    # merge two cliques tables into one
          temp1['value'] = temp1['value_x']+temp1['value_y']                     # add two log factors
          # sum up the new factors
          temp2 = temp1.groupby(sorted(workingVars),as_index=False).agg(logaddsum).drop(columns=['value_x','value_y'])
          lastDF = temp2
      # sum up the results around elimination variable
      sortVar = sorted([q for q in workingVars if q != a])
      if len(sortVar) == 0:                                 # no more variables, break the loop and return Z
        #print(lastDF)
        if len(lastDF['value'])==2:
          VE = numpy.logaddexp(lastDF['value'][0], lastDF['value'][1])
        else:
          VE = lastDF['value'][0]
        break
      newDF = lastDF.groupby(sortVar,as_index=False).agg(logaddsum).drop(columns=[a])
      workingVars.remove(a)                      # drop elimination variable from current clique
      newClique = clique(len(workingVars))       # create new clique function 
      for x in sorted(workingVars):
        newClique.addVar(varList[int(x)])
      newClique.cpd = newDF.shape[0]
      newClique.dot_func = newDF['value'].tolist()
      newClique.df = newDF
      newCliqueList.append(newClique)
      thisCliqueList = newCliqueList                 # update clique functions list to new one

    # weight of sample
    thisW = VE - Q
    sampleT['weight'].append(numpy.exp(thisW))

    estZ = numpy.logaddexp(estZ,thisW)
    estZ = (estZ - numpy.log(N)) / numpy.log(10)

    # ----- update Q if 100 records reached ------
    if (i+1)%100==0:
      totalW = sum(sampleT['weight'])
      for p in XVar:
        cml = 0.0
        lRT = []
        for pp in range(p.d):
          if pp==0:
            lRT.append(0.0)
          else:
            gWeight=0.0
            for px,py in zip(sampleT[p.id],sampleT['weight']):
              if px==pp:
                gWeight += py
            pfr = gWeight/totalW
            cml += pfr
            lRT.append(cml)
        QX[p.id] = lRT
      sampleT = {v.id:[] for v in XVar}
      sampleT['weight']=[]

  return estZ

resultTable = {'Problem':["Grids 14","Grids 15","Grids 16","Grids 17","Grids 18"]}

weightList=[wNum for wNum in wList]
resultTable['weight'] = weightList

for n in nList:
  tNm = "Uniform_"+str(n)
  resultTable[tNm] = []
  vNm = "Adaptive_"+str(n)
  resultTable[vNm] = []


for fListFile,wListNum in zip(fList,wList):
  fUAI=fListFile[0]
  fEvid=fListFile[1]
  fPR=fListFile[2]
  varList, cliqueList, evidVars, baseZ = loadUAI(fUAI,fEvid,fPR)

  w=wListNum
  XVar,tempCliqueList = getCutset(varList,cliqueList,evidVars,w)
  
  for nListCount in nList:
    N=nListCount
    thisUniPro=[]
    tNm = "Uniform_"+str(N)
    vNm = "Adaptive_"+str(N)

    myTracker = {'uTime':[],'uZ':[],'aTime':[],'aZ':[]}
    for rSeedVal in rSeed:
      random.seed(rSeedVal)

      start_time = time.time()
      myUniZ = uniformZ(N,XVar,cliqueList,varList)
      end_time = time.time()
      myTracker['uTime'].append(round(end_time - start_time))
      myTracker['uZ'].append(myUniZ)
      print("*** w:"+str(w)+", N:"+str(N)+", seed:"+str(rSeedVal)+", uniZ:"+str(myUniZ)+", error:"+
            str(baseZ-myUniZ)+", took:"+str(round(end_time - start_time))+"s ***")
        
      start_time = time.time()
      myAdaZ = adaptiveZ(N,XVar,cliqueList,varList)
      end_time = time.time()
      myTracker['aTime'].append(round(end_time - start_time))
      myTracker['aZ'].append(myAdaZ)
      print("*** w:"+str(w)+", N:"+str(N)+", seed:"+str(rSeedVal)+", adaZ:"+str(myAdaZ)+", error:"+
            str(baseZ-myAdaZ)+", took:"+str(round(end_time - start_time))+"s ***")

    myT="Time: "+str(round(numpy.mean(myTracker['uTime']),2))+" +/- "+str(round(numpy.std(myTracker['uTime']),2))
    myError=[(baseZ-eE)/baseZ for eE in myTracker['uZ']]
    myE="Error: "+str(round(numpy.mean(myError),2))+" +/- "+str(round(numpy.std(myError),2))
    resultTable[tNm].append(myT+"\n"+myE)
      
    vyT="Time: "+str(round(numpy.mean(myTracker['aTime']),2))+" +/- "+str(round(numpy.std(myTracker['aTime']),2))
    vyError=[(baseZ-eE)/baseZ for eE in myTracker['aZ']]
    vyE="Error: "+str(round(numpy.mean(vyError),2))+" +/- "+str(round(numpy.std(vyError),2))
    resultTable[vNm].append(vyT+"\n"+vyE)

resultTableDF = pd.DataFrame(resultTable)

resultTableDF.to_excel("result.xlsx",sheet_name='result',index = False)
