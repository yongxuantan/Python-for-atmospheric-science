#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:48:08 2020

@author: Mike
"""

from Position import Position

class Board:
  neighbor = [[8,3,1],[0,4,2],[1,5,13],[0,9,6,4],[3,1,5],[4,7,12,2],[3,10,7],[6,11,5],
              [0,20,9],[8,17,10,3],[9,14,6],[16,12,7],[13,19,13,5],[12,22,2],[17,15,10],
              [14,18,16],[15,19,11],[20,18,14,9],[17,21,19,15],[18,16,12,22],
              [8,17,21],[20,18,22],[21,19,13]]
  mills = [[0,8,20],[3,9,17],[6,10,14],[7,11,16],[5,12,19],[2,13,22],
           [0,1,2],[3,4,5],[8,9,10],[11,12,13],[14,15,16],[17,18,19],[20,21,22],
           [0,3,6],[7,5,2],[20,17,14],[16,19,22]]

  def __init__(self):
    self.positionList = []
  
  def setBoard(self, file):
    for i in range(len(file)):
      pos = Position(i)
      pos.setOwner(file[i])
      self.positionList.append(pos)
    self.assignNeighbor()
  
  def assignNeighbor(self):
    for i in range(len(self.positionList)):
      pos = self.positionList[i]
      n = self.neighbor[i]
      for j in range(len(n)):
        pos.addNeighbor(self.positionList[n[j]])
        
  def printBoard(self):
    b = ""
    for i in range(len(self.positionList)):
      b += self.positionList[i].getOwner()
    return b
        
  def addPos(self,index,player):
    pos = self.positionList[index]
    pos.setOwner(player)
    return self.checkMill(index,player)

  def swapPos(self,prior,post):
    player = self.positionList[prior].getOwner()
    self.positionList[prior].setOwner(self.positionList[post].getOwner())
    self.positionList[post].setOwner(player)
    return self.checkMill(post,player)

  def getMillList(self,index):
    millList = []
    for i in range(len(self.mills)):
      line = self.mills[i]
      if (index in line):
        millList.append(line)
    return millList

  def checkMill(self,index,player):
    isMill = False
    millList = self.getMillList(index)

    for j in range(len(millList)):
      line = millList[j]
      isMill=True
      for k in range(len(line)):
        v = self.positionList[line[k]]
        if player != v.getOwner():
          isMill=False
          break
      if isMill:
        return True
    return isMill

  def soonToMill(self,index,player):
    pts=0
    millList = self.getMillList(index)

    for j in range(len(millList)):
      npie = 0
      nnpie = 0
      xpie = 0
      Xindex = -1
      line = millList[j]
      for k in range(len(line)):
        v = self.positionList[line[k]]
        if v.getOwner() == 'x':
          xpie += 1
          Xindex = v.index
        elif v.getOwner() == player:
          npie += 1
        else:
          nnpie += 1
      if npie == 2 and xpie == 1:
        pts += 5
        vNeighbor = self.positionList[Xindex].getNeighbor()
        for z in vNeighbor:
          if z.getOwner() == player and not z.index in line:
            pts+=20
      elif npie == 2 and nnpie == 1:
        pts += 2
      elif npie == 1 and xpie == 2:
        pts += 4
      elif npie == 1 and nnpie == 2:
        pts += 3
          
    return pts

  def getEmptyPos(self):
    e = []
    for v in self.positionList:
      if v.getOwner() == 'x':
        e.append(v)
    return e 

  def getPos(self, n):
    e = []
    for v in self.positionList:
      if v.getOwner() == n:
        e.append(v)
    return e 

  def getNumMove(self,n):
    e = self.getPos(n)
    c = 0
    for i in e:
      c += len(i.getEmptyNeighbor())
    return c

  def getNum(self,n):
    c = 0
    s = self.printBoard()
    c = s.count(n)
    return c

  def estOpen(self,n,nn):
    return (self.getNum(n)-self.getNum(nn))

  def estMidEnd(self,n,nn):
    if self.getNum(nn) <= 2:
      return 10000
    elif self.getNum(n) <= 2:
      return -10000
    elif self.getNumMove(nn) == 0:
      return 10000
    else:
      h = 1000 * (self.getNum(n) - self.getNum(nn)) - self.getNumMove(nn)
      return h
  
  def estOpenImproved(self,n,nn):
    pts = (self.getNum(n)-self.getNum(nn))*250
    
    L = self.getPos(n)
    for i in L:
      pts += self.soonToMill(i.index,n)
      pts += len(i.getEmptyNeighbor())
      pts += len(self.getMillList(i.index))
      
    M = self.getPos(nn)
    for j in M:
      pts -= self.soonToMill(j.index,n)
      pts -= len(j.getEmptyNeighbor())
      pts -= len(self.getMillList(j.index))
    
    return pts

  def estMidEndImproved(self,n,nn):
    if self.getNum(nn) <= 2:
      return 10000
    elif self.getNum(n) <= 2:
      return -10000
    elif self.getNumMove(nn) == 0:
      return 10000
    else:
      pts = (self.getNum(n)-self.getNum(nn))*250 - self.getNumMove(nn)
    
      L = self.getPos(n)
      for i in L:
        pts += self.soonToMill(i.index,n)
        pts += len(i.getEmptyNeighbor())
        pts += len(self.getMillList(i.index))
      
      M = self.getPos(nn)
      for j in M:
        pts -= self.soonToMill(j.index,n)
        pts -= len(j.getEmptyNeighbor())
        pts -= len(self.getMillList(j.index))
        
      return pts
  
  def visBoard(self):
    L = self.positionList
    print(L[20].occupant+"-----"+L[21].occupant+"-----"+L[22].occupant)
    print("|\\    |    /|")
    print("| "+L[17].occupant+"---"+L[18].occupant+"---"+L[19].occupant+" |")
    print("| |\\  |  /| |")
    print("| "+"| "+L[14].occupant+"-"+L[15].occupant+"-"+L[16].occupant+" |"+" |")
    print("| | |   | | |")
    print(L[8].occupant+"-"+L[9].occupant+"-"+L[10].occupant+"   "+
          L[11].occupant+"-"+L[12].occupant+"-"+L[13].occupant)
    print("| | |   | | |")
    print("| "+"| "+L[6].occupant+"---"+L[7].occupant+" |"+" |")
    print("| |/     \\| |")
    print("| "+L[3].occupant+"---"+L[4].occupant+"---"+L[5].occupant+" |")
    print("|/    |    \\|")
    print(L[0].occupant+"-----"+L[1].occupant+"-----"+L[2].occupant)