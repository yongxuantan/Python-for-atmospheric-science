#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 22:02:27 2020

@author: Mike
"""

#import os
#path = os.getcwd()
#print(path)

#import sys

#if len(sys.argv)<4 :
#	print ("Missing arguments: required <inputfile> <outputfile> depth")
#	sys.exit()
#print("ABOpeningImproved.py program output: \n")

#(sys.argv[1],sys.argv[2],sys.argv[3])

#file0 = open('board1.txt','r')
#file0 = open(sys.argv[1],'r')
#inputBoard = 'xxxxxxxxxxxxxxxxxxxxxxx'
#inputBoard = 'WxWxWxxxxWxxxBBxBxxxBxB'
#inputBoard = file0.read()
#file0.close()
#depth = 4
#depth = int(sys.argv[3])

inputBoard = 'WWBBWxWxWWBxxxBBBBxWBxx'
depth = 2

from Player import Player

p1 = Player('B',depth)
p1.newBoard(inputBoard)
p1.printB()
p1.b.visBoard()
p1.openMoveImproved(float('-inf'),float('-inf'),True)
outputBoard = p1.endAddTurnImproved()

#file1 = open('board2.txt','w')
#file1 = open(sys.argv[2],'w')
#file1.write(outputBoard)
#file1.close()

