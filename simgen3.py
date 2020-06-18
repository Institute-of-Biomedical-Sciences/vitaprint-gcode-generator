#
#  Developed 2020 by Boštjan Vihar (bostjan AT irnas DOT eu)
#

'''

This is a simple g-code generator for making wood-pile scaffold structures using Vitaprint and Planet CNC. Basic shape characteristics of the scaffold, as well as printing parameters can be specified.

USAGE: 
1. Copy simgen.py, xystepcalc.py and circlecalc.py into the same target folder
2. Run script in terminal 
	a) Windows: with the command: python C:\....\simgen.py
	b) Linux:

'''

# FURTHER DEVELOPMENT:
# - rounded edges?

import os
import numpy as np
import matplotlib.pyplot as plt
from xystepcalc import * # import all functions from file
from circlecalc import *

### input values
side_l = float(input("Side length [mm], default = 10: ") or "10")
bar_n = float(input("Number of bars [integer], default = 7: ") or "7")
layer_n = float(input("Number of layers [integer], default = 5: ") or "5")
layer_h = float(input("Layer height [mm], default = 0.2: ") or "0.2")
feedrate = float(input("Printing speed [mm/min], default = 500: ") or "500")
shape = input("Cross section shape square (s) or circle (c), default = s: ") or "s"
drive = input("Extrusion drive pneumatic (p) or mechanical (m), default = p: ") or "p"
if drive == "m":
	dist_ext = float(input("Extrusion [mm] per 10mm distance, default = 0.1: ") or "0.1")
	flow = input("Enable flow control [y/n]: ")	or "n"
	if flow == 'y':
		flow = '* #<_hw_jogpot>/511'
	else:
		flow = ''
	fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_a'+str(round(dist_ext*100))+'e-2'
else:
	fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_pneum'

### default values
ramp = 0.05 #ramp/retraction extrusion
zsafe = 2 # safe height after print
sdist = 2 # skirt distance from scaffold

#### determine writing direction depending on number of crossing bars
if bar_n % 2 == 0:
	x,y = xy4(side_l,bar_n) # if number of bars is even, you require 4 steps to return to 0,0
	if shape == 'c': # if shape is a circle, recalculate x/y coordinates
		x,y = circ4(side_l,x,y)
	else:
		pass
	xn = 4

else:
	x,y = xy2(side_l,bar_n) # if number of bars is odd, require 2 steps to return to 0,0
	if shape == 'c': # if shape is a circle, recalculate x/y coordinates
		x,y = circ2(side_l,x,y)
	else:
		pass
	xn = 2

#### CALCULATE COORDINATES ##################################################################
r = (layer_n/xn) - int(layer_n/xn) # residual fraction of x/y array
# calculate all x coordinates
xt = np.tile(x,(int(layer_n/xn),1))
x = np.append(xt,x[:int(r*xn)], axis=0)
x = np.round(x,decimals=6)

# calculate all y coordinates
yt = np.tile(y,(int(layer_n/xn),1))
y = np.append(yt,y[:int(r*xn)], axis=0)
y = np.round(y,decimals=6)

#### CALCULATE DISTANCES BETWEEN POINTS
xflat=np.append([0],np.ravel(x),axis=0) #flatten x array and add a 0 at the beginning
yflat=np.append([0],np.ravel(y),axis=0)

n = np.size(xflat)
d = np.sqrt((xflat[0:n-1]-xflat[1:n])**2+(yflat[0:n-1]-yflat[1:n])**2) #calculate distances between all points

#### CALCULATE EXTRUSION "A" and reshape to x/y formats
# aflat = d/10*dist_ext 
# a = np.reshape(aflat,np.shape(x)) #reshape to x/y formats
# a = np.round(a,decimals=6)

### CALCULATE SKIRT
xskirt = np.array([-sdist, side_l+sdist, side_l+sdist, -sdist, -sdist,0])
yskirt = np.array([-sdist, -sdist, side_l+sdist, side_l+sdist, -sdist,0])

# askirt = np.full((1,4),(side_l+sdist)/10*dist_ext)
# askirt = np.append([0],np.ravel(askirt),axis=0)
# askirt = np.append(np.ravel(askirt),[0],axis=0)



#### WRITING TO FILE #####################################################################

def pneumatic():
	# starting g-code
	f = open(fname+'.gcode', "w")
	f.write('%\n') # first line of g-code
	f.write('G92\tX0\tY0\n') #set xy coordinates to 0
	f.write('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0
	# f.write('G1\tA[#<_a> +{0}] ;ramp\n\n'.format(ramp)) #ramp


	# skirt
	f.write('M8\n') #open valve
	for i in range(0,np.size(xskirt)):
		skirt = 'G1\tX{0}\tY{1}\n'.format(xskirt[i],yskirt[i])
		f.write(skirt)
	f.write('M9\n') #close valve
	f.write('\n') #empty line

	# main blocks     # sample line G1 X4.8 Y1.5 A[#<_a> + 0.00038 * #<_hw_jogpot>/511]
	h= np.shape(x)[0] # array height
	w= np.shape(x)[1] # array width
	g = 3 #first direction of rotation

	if shape == 'c': # if shape is a circle, draw circles
		for j in range(0,h):
			f.write('M8\n') #valve
			for i in range(0,w):
				if i % 2 == 0:
					vrstica = 'G1\tX{0}\tY{1}\n'.format(x[j,i],y[j,i])
				else:
					vrstica = 'G{3}\tX{0}\tY{1}\tR{2}\n'.format(x[j,i],y[j,i],side_l/2,g)
					if g == 3: # switch G2/3 direction
						g = 2
					else:
						g = 3
				f.write(vrstica)
			f.write('M9\n') #valve
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			f.write(zline)
			if g == 3: # switch G2/3 direction
				g = 2
			else:
				g = 3
			if j<h-1:
				jump = 'G{3}\tX{0}\tY{1}\tR{2}\tF1600\n'.format(x[j+1,0],y[j+1,0],side_l/2,g) #take FIRST xy elements of NEXT BLOCK
				f.write(jump)
				f.write('G1\tF{0}\n'.format(feedrate))
			else:
				pass
	else: # draw squares
		for j in range(0,h):
			f.write('M8\n') #valve
			for i in range(0,w):
				vrstica = 'G1\tX{0}\tY{1}\n'.format(x[j,i],y[j,i])
				f.write(vrstica)
			f.write('M9\n') #valve
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			f.write(zline)

	### end g-code
	# f.write('G1\tA[#<_a> -{0}] ;retract\n'.format(ramp)) #retract
	f.write('G1\tZ[#<_z> +{0}] ;go to safe height\n'.format(zsafe)) #go to safe height
	f.write('G1\tX{0}\tY{1} ;go to next xy position\n'.format(side_l+5,0)) #go to next xy position
	f.write('%')
	f.close()
	
def piston():
	#### CALCULATE EXTRUSION "A" and reshape to x/y formats
	aflat = d/10*dist_ext 
	a = np.reshape(aflat,np.shape(x)) #reshape to x/y formats
	a = np.round(a,decimals=6)

	### CALCULATE SKIRT
	xskirt = np.array([-sdist, side_l+sdist, side_l+sdist, -sdist, -sdist,0])
	yskirt = np.array([-sdist, -sdist, side_l+sdist, side_l+sdist, -sdist,0])

	askirt = np.full((1,4),(side_l+sdist)/10*dist_ext)
	askirt = np.append([0],np.ravel(askirt),axis=0)
	askirt = np.append(np.ravel(askirt),[0],axis=0)

	# starting g-code
	f = open(fname+'.gcode', "w")
	f.write('%\n') # first line of g-code
	f.write('G92\tX0\tY0\n') #set xy coordinates to 0
	f.write('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0
	f.write('G1\tA[#<_a> +{0}] ;ramp\n\n'.format(ramp)) #ramp

	# skirt
	for i in range(0,np.size(xskirt)):
		skirt = 'G1\tX{0}\tY{1}\tA[#<_a> +{2}]\n'.format(xskirt[i],yskirt[i],askirt[i])
		f.write(skirt)
	f.write('\n') #empty line

	# main blocks     # sample line G1 X4.8 Y1.5 A[#<_a> + 0.00038 * #<_hw_jogpot>/511]
	h= np.shape(x)[0] # array height
	w= np.shape(x)[1] # array width
	g = 3 #first direction of rotation

	if shape == 'c': # if shape is a circle, draw circles
		for j in range(0,h):
			for i in range(0,w):
				if i % 2 == 0:
					vrstica = 'G1\tX{0}\tY{1}\tA[#<_a> +{2}'.format(x[j,i],y[j,i],a[j,i])+flow+']\n'
				else:
					vrstica = 'G{4}\tX{0}\tY{1}\tR{3}\tA[#<_a> +{2}'.format(x[j,i],y[j,i],a[j,i],side_l/2,g)+flow+']\n'
					if g == 3: # switch G2/3 direction
						g = 2
					else:
						g = 3
				f.write(vrstica)
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			f.write(zline)
			if g == 3: # switch G2/3 direction
				g = 2
			else:
				g = 3
			if j<h-1:
				jump = 'G{3}\tX{0}\tY{1}\tR{2}\tF1600\n'.format(x[j+1,0],y[j+1,0],side_l/2,g) #take FIRST xy elements of NEXT BLOCK
				f.write(jump)
				f.write('G1\tF{0}\n'.format(feedrate))
			else:
				pass
	else: # draw squares
		for j in range(0,h):
			for i in range(0,w):
				vrstica = 'G1\tX{0}\tY{1}\tA[#<_a> +{2}'.format(x[j,i],y[j,i],a[j,i])+flow+']\n'
				f.write(vrstica)
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			f.write(zline)

	### end g-code
	f.write('G1\tA[#<_a> -{0}] ;retract\n'.format(ramp)) #retract
	f.write('G1\tZ[#<_z> +{0}] ;go to safe height\n'.format(zsafe)) #go to safe height
	f.write('G1\tX{0}\tY{1} ;go to next xy position\n'.format(side_l+5,0)) #go to next xy position
	f.write('%')
	f.close()
	
###### EXECUTE G-CODE GENERATOR
if drive == "m":
	piston()
else:
	pneumatic()