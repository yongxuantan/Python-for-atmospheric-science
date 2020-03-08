#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri Feb 14 01:28:11 2020

@author: Yongxuan Tan
"""

import os
import sys
import numpy
import pandas as pd

# house keeping to make sure required parameters had been given
if len(sys.argv)<2 :
	print ("Missing arguments: required <UAI file path> <evidence file path>, terminating program...")
	sys.exit()
if os.path.isfile(sys.argv[1])==False:
    print("The UAI file path you provided is invalid or file not exist.")
    print("terminating program...")
    sys.exit()
if  os.path.isfile(sys.argv[2])==False:
    print("The evidence file path you provided is invalid or file not exist.")
    print("terminating program...")
    sys.exit()
print("hw2.py program output: \n")

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

f = open(sys.argv[1])

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

# take a look at clique functions to make sure import was correct
print(cliqueList)

"""Load evidence file"""

fevid = open(sys.argv[2])

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

# check clique functions again to make sure evidence were calculated correctly
print(cliqueList)

"""Calculate elimination order using min-degree"""

minOrder = {}

for b in varList:           
  vID = b.id
  if (vID not in evidVars):     # loop through all non-evidence variables
    clqCnt = 0
    for c in cliqueList:
      if c.contain(vID):        # increase count if variable found in clique function
        clqCnt += 1
    minOrder[vID] = clqCnt

# look at order
minOrderSorted = sorted(minOrder.items(), key=lambda x: x[1])
minOrderSortedList = [a for a,b in minOrderSorted]

minOrderSortedList = minOrderSortedList + evidVars         # add evidence variables to the end

"""start bucket elimination"""

for a in minOrderSortedList:

  newCliqueList = []              # store irrelevant cliques
  workingCliqueList = []          # store relevant cliques

  for h in cliqueList:            # loop through all cliques to find the ones we need
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
      temp1['value'] = temp1['value_x']*temp1['value_y']                     # multiply two factors

      # sum up the new factors
      temp2 = temp1.groupby(sorted(workingVars),as_index=False).agg('sum').drop(columns=['value_x','value_y'])
      lastDF = temp2

  # sum up the results around elimination variable
  sortVar = sorted([q for q in workingVars if q != a])
  if len(sortVar) == 0:                                 # no more variables, break the loop and return Z
    print(lastDF)
    Z = lastDF['value'].sum()
    break
  newDF = lastDF.groupby(sortVar,as_index=False).agg('sum').drop(columns=[a])

  workingVars.remove(a)                      # drop elimination variable from current clique

  newClique = clique(len(workingVars))       # create new clique function 
  for x in sorted(workingVars):
    newClique.addVar(varList[int(x)])

  newClique.cpd = newDF.shape[0]
  newClique.dot_func = newDF['value'].tolist()
  newClique.df = newDF
  newCliqueList.append(newClique)

  cliqueList = newCliqueList                 # update clique functions list to new one

  # check progress after each variable is eliminated
  print("\n" + a + " is eliminated:")
  #print(cliqueList)

PR = numpy.round(numpy.log10(Z),decimals=4)

print("PR is: " + str(PR))

