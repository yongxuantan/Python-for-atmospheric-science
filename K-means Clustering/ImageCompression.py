#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 15:28:39 2019

@author: Mike
"""

from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
import random

K_list = [2,5,10,15,20]

# maximum iteration before we stop
max_iter = 100

penguin_img = plt.imread("Penguins.jpg")
p_output = ['penguins_k2.jpg','penguins_k5.jpg','penguins_k10.jpg',
            'penguins_k15.jpg','penguins_k20.jpg']

koala_img = plt.imread("Koala.jpg")
k_output = ['koala_k2.jpg','koala_k5.jpg','koala_k10.jpg','koala_k15.jpg','koala_k20.jpg']

# return list of centroid group assignment for each pixel
def findClosestCentroids(X, centroids, K):
    
    # initialize centroid group assignment
    idx = np.zeros((X.shape[0],1),dtype=int)
    
    # loop through each pixel
    for r in range(X.shape[0]):
        # assign to group 0 at first
        distance = np.sum((X[r] - centroids[0]) ** 2)
        idx[r] = 0
        
        # calculate distance from other centroid groups
        for g in range(1,K):
            dist2 = np.sum((X[r] - centroids[g]) ** 2)
            
            # update group if found a closer candidate
            if dist2 < distance:
                distance = dist2
                idx[r] = g
    return idx
    
# return the new centroid average values after updated centroid group assignment
def computeCentroids(X, idx, K, old_centroids):
    
    # initialize centroid groups
    centroids = np.zeros((K,X.shape[1]))
    
    # loop through each group
    for c in range(K):
        
        # get index list of the assigned group
        rowx = idx == c
        
        # get sum of all values for this centroid group, group by R, G, B columns
        sumx = np.sum(rowx * X, 0)
        
        # update centroid value, if no row assigned to this group, use centroid from last run
        if np.sum(rowx)>0:
            centroids[c] = sumx/np.sum(rowx)
        else:
            centroids[c] = old_centroids[c]
    return centroids


def compress(K_list, max_iter, in_image, out_names):
    
    img1=in_image
    img_size = img1.shape
    
    # stack the image into R, G, B columns
    X = np.reshape(img1, (img_size[0]*img_size[1], 3))
    random.seed()
    
    # loop through each K-cluster choice and save a new image after each iteration
    for K,fname in zip(K_list,out_names):
        
        # initialize centroids to random pixcel
        centroids2 = X[random.sample(range(X.shape[0]),K),:]
        
        # initialize centroid group assignment
        idx = np.zeros((X.shape[0],1),dtype=int)
        
        # use to track if converges
        last_idx = idx
        
        # start grouping
        for i in range(max_iter):
            idx = findClosestCentroids(X, centroids2, K)
            centroids2 = computeCentroids(X, idx, K, centroids2)
            print('Grouping '+str(K)+' clusters, on iteration '+str(i)+' out of '+str(max_iter-1))
            if np.all(last_idx==idx):
                break
            else:
                last_idx=idx
        
        # recover X values by matching centroid group assignment to the centroid value
        X_recovered = [centroids2[v] for v in idx]
        
        # put back into original image dimension
        Y_recovered = np.reshape(X_recovered, (img_size[0],img_size[1],3))
        
        # drop the decimal values
        z = (Y_recovered).astype(np.uint8)
        
        img5 = Image.fromarray(z)
        img5.save(fname)

print('Compressing Penguin image --------------------------')
compress(K_list, max_iter, penguin_img, p_output)
print('Compressing Koala image --------------------------')
compress(K_list, max_iter, koala_img, k_output)