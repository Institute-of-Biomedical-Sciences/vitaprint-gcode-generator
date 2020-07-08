#############################################################
#															#
# 2/4 step xy coordinates calculation of square structures	#
#															#
#############################################################

import os
import numpy as np

def xy2(side_l,bar_n):

	n = bar_n+1 #number of increments
	d = side_l/n #distance between two bars

	ni = np.repeat(np.arange(0,n+1,1),2) #make array with double indexes from 0 to n+1
	nev = (ni%2==0).astype(int) #make a 1/0 array of even indexes

## there...
	x1=n*d*(nev)[:-1] #make array for x axis, crossing the structure every secong step: every even/odd value is 1/0, multiplied by length of structure
	y1=d*(ni[1:]) #make array for y axis, growing incrementally

## and back again
	x2 = np.append(np.flip(y1)[1:],[0]) #y1 array in reversed order with app. finish point
	y2 = np.append(np.flip(x1)[1:],[0]) #x1 array in reversed order with app. finish point
## combine
	x = np.array([x1,x2])
	y = np.array([y1,y2])
	return x,y

def xy4(side_l,bar_n):

	n = bar_n+1 #number of increments
	d = side_l/n #distance between two bars

	ni = np.repeat(np.arange(0,n+1,1),2) #make array with double indexes from 0 to n+1
	nev = (ni%2==0).astype(int) #make a 1/0 array of even indexes
	
## step 1
	x1=n*d*(nev[:-1]) #make array for x axis, crossing the structure every secong step: every even/odd value is 1/0, multiplied by side_l
	y1=d*(ni[1:]) #make array for y axis, growing incrementally

## step 2
	x2 = d*(ni[1:]) #
	y2 = n*d*np.flip(nev[1:]) # 

## step 3
	x3 = np.flip(n*d*(nev[1:])) #
	y3 = np.flip(d*(ni[:-1]))

## step 4
	x4 = np.flip(d*ni[:-1])# 
	y4 = n*d*nev[:-1]#
	
## combine
	x = np.array([x1,x2,x3,x4])
	y = np.array([y1,y2,y3,y4])
	return x,y
