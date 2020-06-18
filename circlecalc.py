#############################################################
#															#
# 2/4 step xy coordinates calculation of square structures	#
#															#
#############################################################

import os
import numpy as np

def circ2(side_l,x,y):
### new point calculations
	d = side_l #simplify syntax

	#for x
	l = np.sqrt((d/2)**2-(d/2-y[0])**2) # calculate distances of x relative from vertical going through center
	l[np.where(x[0]==0)]=-l[np.where(x[0]==0)] # determine where to add/subtract values from middle
	x[0] = l + d/2 # subtract/add distances from middle

	# for y
	h = np.sqrt((d/2)**2-(d/2-x[1])**2)
	h[np.where(y[1]==0)]=-h[np.where(y[1]==0)]
	y[1] = h + d/2
	
	x = x[:,:-1] #remove last element of each row
	y = y[:,:-1]
	return x,y
	
def circ4(side_l,x,y):
	d = side_l

	l = np.sqrt((d/2)**2-(d/2-y[0])**2)
	l[np.where(x[0]==0)]=-l[np.where(x[0]==0)]
	x[0] = l + d/2

	h = np.sqrt((d/2)**2-(d/2-x[1])**2)
	h[np.where(y[1]==0)]=-h[np.where(y[1]==0)]
	y[1] = h + d/2

	x[2] = h + d/2
	y[3] = l + d/2
	
	x = x[:,:-1]
	y = y[:,:-1]
	return x,y