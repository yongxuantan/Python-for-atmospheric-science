#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 21:49:18 2020

@author: Mike
"""

class Position:

  def __init__(self, id):
    self.index = id
    self.occupant = 'x'
    self.neighbor = []

  def setOwner(self, owner):
    self.occupant = owner
  
  def getOwner(self):
    return self.occupant

  def addNeighbor(self, n):
    self.neighbor.append(n)

  def getNeighbor(self):
    return self.neighbor
  
  def getEmptyNeighbor(self):
    n = []
    for i in range(len(self.neighbor)):
      p = self.neighbor[i]
      if p.getOwner() == 'x':
        n.append(p)
    return n

  def getSameNeighbor(self):
    n = []
    for i in range(len(self.neighbor)):
      p = self.neighbor[i]
      if p.getOwner() == self.occupant:
        n.append(p)
    return n

  def printNeighbor(self):
    b = ""
    for i in range(len(self.neighbor)):
      b += self.neighbor[i].getOwner()
    return b
  
  def __repr__(self):
    return str(self.index)+":"+self.getOwner()