#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:44:30 2020

@author: Mike
"""

from Board import Board
import random
import copy

class Player:
  def __init__(self,n,d):
    self.name = n
    self.depth = d
    self.searchC = 0
    self.b = Board()
    if n=='W':
      self.oppName = 'B'
    elif n=='B':
      self.oppName = 'W'
  
  def board(self,bo):
    self.b=bo
    
  def newBoard(self,f):
    self.b.setBoard(f)

  def printB(self):
    print("Board Position: "+self.b.printBoard())
    
  def openMove(self,minp,minopp,prune):
    if len(self.b.getPos(self.name)) < 9:
      m, c = self.generateAdd(minp,minopp,prune)
      r = self.b.addPos(m.index, self.name)
      self.searchC = c
      if r:
        self.removeOpp(self.b,self.oppName, True)
    else:
      #print("move to mid or end game")
      self.searchC = 0
      
  def gameMove(self,minp,minopp,prune):
    if len(self.b.getPos(self.name)) == 3:
      b,a,c = self.generateHopping(minp,minopp,prune)
    elif len(self.b.getPos(self.name)) > 3:
      b,a,c = self.generateMove(minp,minopp,prune)
    else:
      print("Player " + self.name + " lost.")
      return

    self.searchC = c
    r = self.b.swapPos(b.index,a.index)
    if r:
      self.removeOpp(self.b,self.oppName, False)
      
  def removeOpp(self, bb, oN, op):
    oppList = bb.getPos(oN)

    if len(oppList) <= 3:
      random.choice(oppList).setOwner('x')
    else:
      cleanOppList=[]
      heuristic = []

      for i in oppList:
        if not (bb.checkMill(i.index,oN)):
          cleanOppList.append(i)
          tempb = copy.deepcopy(bb)
          tempb.positionList[i.index].setOwner('x')
          if op:
            frnd = tempb.estOpen(self.name,self.oppName)
          else:
            frnd = tempb.estMidEnd(self.name,self.oppName)
          heuristic.append(frnd)

      if len(cleanOppList)>0:
        maxIndex = heuristic.index(max(heuristic))
        cleanOppList[maxIndex].setOwner('x')

  def generateAdd(self,minp,minopp,prune):
    evalCount = 0
    L = self.b.getEmptyPos()
    heuristic = []

    if len(L) == 0:
      print("Player " + self.name + " lost.")

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      evalCount += 1
      tempb = copy.deepcopy(self.b)

      if tempb.addPos(i.index,self.name):
        self.removeOpp(tempb,self.oppName, True)

      myScore = tempb.estOpen(self.name,self.oppName)
      oppScore = tempb.estOpen(self.oppName,self.name)

      # pruning
      if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
        return i, evalCount

      if self.depth>1:
        # switch player and play
        opp = Player(self.oppName,self.depth-1)
        opp.board(tempb)

        opp.openMove(oppMinPossible,myMinPossible,prune)
        evalCount += opp.searchC

        scoreAfter = opp.b.estOpen(self.name,self.oppName)
        if scoreAfter > myMinPossible:
          myMinPossible=scoreAfter
        
      heuristic.append(tempb.estOpen(self.name,self.oppName))

    maxIndex = heuristic.index(max(heuristic))
    return L[maxIndex], evalCount

  def generateMove(self,minp,minopp,prune):
    L = self.b.getPos(self.name)
    evalCount = 0
    heuristicI = []
    heuristicN = []
    movable = []

    if len(L) < 3:
      print("Player " + self.name + " lost.")

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      pts = 0
      
      Q = i.getEmptyNeighbor()
      heuristicJ = []

      if len(Q) == 0:
        continue
      else:
        for j in Q:
          tempb = copy.deepcopy(self.b)
          evalCount += 1

          if tempb.swapPos(i.index,j.index):
            self.removeOpp(tempb,self.oppName, False)

          myScore = tempb.estMidEnd(self.name,self.oppName)
          oppScore = tempb.estMidEnd(self.oppName,self.name)
          # pruning
          if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
            heuristicJ.append(myScore)
            break
          
          if self.depth>1:
            # switch player and play
            opp = Player(self.oppName,self.depth-1)
            opp.board(tempb)
            opp.gameMove(oppMinPossible,myMinPossible,prune)
            evalCount += opp.searchC

            scoreAfter = opp.b.estMidEnd(self.name,self.oppName)
            if scoreAfter > myMinPossible:
              myMinPossible=scoreAfter
              
          heuristicJ.append(tempb.estMidEnd(self.name, self.oppName))

      maxHeuristicJ = max(heuristicJ)
      maxIndexJ = heuristicJ.index(maxHeuristicJ)
      heuristicI.append(maxHeuristicJ+pts)
      heuristicN.append(Q[maxIndexJ])
      movable.append(i)

    maxIndex = heuristicI.index(max(heuristicI))
    return movable[maxIndex], heuristicN[maxIndex], evalCount

  def generateHopping(self,minp,minopp,prune):
    L = self.b.getPos(self.name)
    Q = self.b.getEmptyPos()
    evalCount = 0
    heuristicI = []
    heuristicN = []

    if len(L) < 3:
      print("Player " + self.name + " lost.")
      return

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      pts = 0
      
      heuristicJ = []

      if len(Q) == 0:
        continue
      else:
        for j in Q:
          tempb = copy.deepcopy(self.b)
          evalCount += 1

          if tempb.swapPos(i.index,j.index):
            self.removeOpp(tempb,self.oppName, False)
          
          myScore = tempb.estMidEnd(self.name,self.oppName)
          oppScore = tempb.estMidEnd(self.oppName,self.name)
          # pruning
          if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
            heuristicJ.append(myScore)
            break
          
          if self.depth>1:
            # switch player and play
            opp = Player(self.oppName,self.depth-1)
            opp.board(tempb)
            opp.gameMove(oppMinPossible,myMinPossible,prune)
            evalCount += opp.searchC

            scoreAfter = opp.b.estMidEnd(self.name,self.oppName)
            if scoreAfter > myMinPossible:
              myMinPossible=scoreAfter

          heuristicJ.append(tempb.estMidEnd(self.name,self.oppName))

      maxHeuristicJ = max(heuristicJ)
      maxIndexJ = heuristicJ.index(maxHeuristicJ)
      heuristicI.append(maxHeuristicJ+pts)
      heuristicN.append(Q[maxIndexJ])

    maxIndex = heuristicI.index(max(heuristicI))
    return L[maxIndex], heuristicN[maxIndex], evalCount

  def openMoveImproved(self,minp,minopp,prune):
    if len(self.b.getPos(self.name)) < 9:
      m, c = self.generateAddImproved(minp,minopp,prune)
      r = self.b.addPos(m.index, self.name)
      self.searchC = c
      if r:
        self.removeOppImproved(self.b,self.oppName, True)
    else:
      #print("move to mid or end game")
      self.searchC = 0
      
  def gameMoveImproved(self,minp,minopp,prune):
    if len(self.b.getPos(self.name)) == 3:
      b,a,c = self.generateHoppingImproved(minp,minopp,prune)
    elif len(self.b.getPos(self.name)) > 3:
      b,a,c = self.generateMoveImproved(minp,minopp,prune)
    else:
      print("Player " + self.name + " lost.")
      return

    self.searchC = c
    r = self.b.swapPos(b.index,a.index)
    if r:
      self.removeOppImproved(self.b,self.oppName, False)
      
  def removeOppImproved(self, bb, oN, op):
    oppList = bb.getPos(oN)

    if len(oppList) <= 3:
      random.choice(oppList).setOwner('x')
      #print("Player " + self.name + " win.")
    else:
      cleanOppList=[]
      heuristic = []

      for i in oppList:
        if not (bb.checkMill(i.index,oN)):
          cleanOppList.append(i)
          tempb = copy.deepcopy(bb)
          tempb.positionList[i.index].setOwner('x')
          if op:
            frnd = tempb.estOpenImproved(self.oppName,self.name)
          else:
            frnd = tempb.estMidEndImproved(self.oppName,self.name)
            #print("removing "+str(i)+" w/ score: "+str(frnd))
          heuristic.append(frnd)

      if len(cleanOppList)>0:
        maxIndex = heuristic.index(min(heuristic))
        cleanOppList[maxIndex].setOwner('x')

  def generateAddImproved(self,minp,minopp,prune):
    evalCount = 0
    L = self.b.getEmptyPos()
    heuristic = []

    if len(L) == 0:
      print("Player " + self.name + " lost.")

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      evalCount += 1
      tempb = copy.deepcopy(self.b)

      if tempb.addPos(i.index,self.name):
        self.removeOppImproved(tempb,self.oppName, True)

      myScore = tempb.estOpenImproved(self.name,self.oppName)
      oppScore = tempb.estOpenImproved(self.oppName,self.name)

      # pruning
      if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
        return i, evalCount

      if self.depth>1:
        # switch player and play
        opp = Player(self.oppName,self.depth-1)
        opp.board(tempb)

        opp.openMoveImproved(oppMinPossible,myMinPossible,prune)
        evalCount += opp.searchC

        scoreAfter = opp.b.estOpenImproved(self.name,self.oppName)
        if scoreAfter > myMinPossible:
          myMinPossible=scoreAfter
        
      heuristic.append(tempb.estOpenImproved(self.name,self.oppName))

    maxIndex = heuristic.index(max(heuristic))
    return L[maxIndex], evalCount

  def generateMoveImproved(self,minp,minopp,prune):
    L = self.b.getPos(self.name)
    evalCount = 0
    heuristicI = []
    heuristicN = []
    movable = []

    if len(L) < 3:
      print("Player " + self.name + " lost.")

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      pts = 0
      
      Q = i.getEmptyNeighbor()
      heuristicJ = []

      if len(Q) == 0:
        continue
      else:
        for j in Q:
          tempb = copy.deepcopy(self.b)
          evalCount += 1

          if tempb.swapPos(i.index,j.index):
            self.removeOppImproved(tempb,self.oppName, False)

          myScore = tempb.estMidEndImproved(self.name,self.oppName)
          oppScore = tempb.estMidEndImproved(self.oppName,self.name)
          # pruning
          if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
            heuristicJ.append(myScore)
            break
          
          if self.depth>1:
            # switch player and play
            opp = Player(self.oppName,self.depth-1)
            opp.board(tempb)
            
            opp.gameMoveImproved(oppMinPossible,myMinPossible,prune)
            evalCount += opp.searchC

            scoreAfter = opp.b.estMidEndImproved(self.name,self.oppName)
            if scoreAfter > myMinPossible:
              myMinPossible=scoreAfter
              
          heuristicJ.append(tempb.estMidEndImproved(self.name,self.oppName))

      maxHeuristicJ = max(heuristicJ)
      maxIndexJ = heuristicJ.index(maxHeuristicJ)
      heuristicI.append(maxHeuristicJ+pts)
      heuristicN.append(Q[maxIndexJ])
      movable.append(i)

    maxIndex = heuristicI.index(max(heuristicI))
    return movable[maxIndex], heuristicN[maxIndex], evalCount

  def generateHoppingImproved(self,minp,minopp,prune):
    L = self.b.getPos(self.name)
    Q = self.b.getEmptyPos()
    evalCount = 0
    heuristicI = []
    heuristicN = []

    if len(L) < 3:
      print("Player " + self.name + " lost.")
      return

    myMinPossible = minp
    oppMinPossible = minopp
    for i in L:
      pts = 0
      
      heuristicJ = []

      if len(Q) == 0:
        continue
      else:
        for j in Q:
          tempb = copy.deepcopy(self.b)
          ptsJ = 0
          evalCount += 1

          if tempb.swapPos(i.index,j.index):
            self.removeOppImproved(tempb,self.oppName, False)
          
          myScore = tempb.estMidEndImproved(self.name,self.oppName)
          oppScore = tempb.estMidEndImproved(self.oppName,self.name)
          # pruning
          if prune and (myScore < myMinPossible or oppScore < oppMinPossible):
            heuristicJ.append(myScore)
            break
          
          if self.depth>1:
            # switch player and play
            opp = Player(self.oppName,self.depth-1)
            opp.board(tempb)
            
            opp.gameMoveImproved(oppMinPossible,myMinPossible,prune)
            evalCount += opp.searchC

            scoreAfter = opp.b.estMidEndImproved(self.name,self.oppName)
            if scoreAfter > myMinPossible:
              myMinPossible=scoreAfter

          heuristicJ.append(ptsJ+tempb.estMidEndImproved(self.name,self.oppName))

      maxHeuristicJ = max(heuristicJ)
      maxIndexJ = heuristicJ.index(maxHeuristicJ)
      heuristicI.append(maxHeuristicJ+pts)
      heuristicN.append(Q[maxIndexJ])

    maxIndex = heuristicI.index(max(heuristicI))
    return L[maxIndex], heuristicN[maxIndex], evalCount

  def endAddTurn(self):
    print("======================== end turn ============================")
    self.printB()
    print("Positions evaluated by static estimation: "+str(self.searchC))
    print("MINIMAX estimate: " + str(self.b.estOpen(self.name,self.oppName)))
    self.b.visBoard()
    return self.b.printBoard()

  def endAddTurnImproved(self):
    print("======================== end turn ============================")
    self.printB()
    print("Positions evaluated by static estimation: "+str(self.searchC))
    print("MINIMAX estimate: " + str(self.b.estOpenImproved(self.name,self.oppName)))
    self.b.visBoard()
    return self.b.printBoard()

  def endGameTurn(self):
    print("======================== end mid/end game turn ==========================")
    self.printB()
    print("Positions evaluated by static estimation: "+str(self.searchC))
    print("MINIMAX estimate: " + str(self.b.estMidEnd(self.name,self.oppName)))
    self.b.visBoard()
    return self.b.printBoard()

  def endGameTurnImproved(self):
    print("======================== end mid/end game turn ==========================")
    self.printB()
    print("Positions evaluated by static estimation: "+str(self.searchC))
    print("MINIMAX estimate: " + str(self.b.estMidEndImproved(self.name,self.oppName)))
    self.b.visBoard()
    return self.b.printBoard()
