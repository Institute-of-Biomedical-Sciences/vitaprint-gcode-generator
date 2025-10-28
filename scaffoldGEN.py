#
#  Developed 2020 by Boštjan Vihar (bostjan AT irnas DOT eu)
#

'''

This is a simple g-code generator for making wood-pile scaffold structures using Vitaprint and Planet CNC. Basic shape characteristics of the scaffold, as well as printing parameters can be specified.

USAGE: 
1. Copy scaffoldGEN.py to target directory and uncomment input/output commands
2. Run script in terminal 

'''

# FURTHER DEVELOPMENT:
# - rounded edges?

import os
import numpy as np

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

'''
### INPUT VALUES - uncomment to use as standalone
side_l = float(input("Side length [mm], default = 10: ") or "10")
bar_n = float(input("Number of bars [integer], default = 7: ") or "7")
layer_n = float(input("Number of layers [integer], default = 5: ") or "5")
layer_h = float(input("Layer height [mm], default = 0.2: ") or "0.2")
feedrate = float(input("Printing speed [mm/min], default = 500: ") or "500")
shape = input("Cross section shape square (s) or circle (c), default = s: ") or "s"
drive = input("Extrusion drive pneumatic (p) or mechanical (m), default = p: ") or "p"
if drive == "m":
	dist_ext = float(input("Extrusion [mm] per 10mm distance, default = 0.1: ") or "0.1")
	ramp = float(input("Ramp/retraction [mm], default = 0.05: ") or "0.05")
	flow = input("Enable flow control [y/n], default = n: ") or "n"
	if flow == 'y':
		flow = '* #<_hw_jogpot>/511'
	else:
		flow = ''
e_num = input("Extruder number (1,2 or 3), default = 1: ") or "1"
zsafe = float(input("Safe height after print [mm], default = 2: ") or "2")
skirt_i = input("Add skirt [y/n], default = n: ") or "n"
if skirt_i == "y":
	sdist = float(input("Skirt distance from scaffold [mm], default = 2: ") or "2")
else:
	pass



### GENERATE FILENAME
if drive == "m":
	fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_a'+str(round(dist_ext*100))+'e-2'
else:
	fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_pneum'
'''


#### CALCULATE COORDINATES ##################################################################
def coordinates(side_l,bar_n,shape,layer_n):
	
	if bar_n % 2 == 0:
		x,y = xy4(side_l,bar_n) # if number of bars is even, you require 4 steps to return to 0,0
		if shape == 'cylinder': # if shape is a circle, recalculate x/y coordinates
			x,y = circ4(side_l,x,y)
		else:
			pass
		xn = 4

	else:
		x,y = xy2(side_l,bar_n) # if number of bars is odd, require 2 steps to return to 0,0
		if shape == 'cylinder': # if shape is a circle, recalculate x/y coordinates
			x,y = circ2(side_l,x,y)
		else:
			pass
		xn = 2

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

	return x,y,n,d

### SKIRT coordinates
def skirt_c(sdist,side_l):
	xskirt = np.array([-sdist, side_l+sdist, side_l+sdist, -sdist, -sdist,0])
	yskirt = np.array([-sdist, -sdist, side_l+sdist, side_l+sdist, -sdist,0])
	return xskirt, yskirt

### ROTATIONS
def xy2(side_l,bar_n): #2-STEP ROTATION

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

def xy4(side_l,bar_n): #4-STEP ROTATION

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


### CYLINDRICAL SCAFFOLDS
def circ2(side_l,x,y): #2-STEP ROTATION
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
	
def circ4(side_l,x,y): #4-STEP ROTATION
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


#### WRITING TO FILE #####################################################################

def pneumatic(fname,x,y,n,d,shape,side_l,layer_h,layer_n,skirt_i,sdist,feedrate,zsafe,e_num,e_val):
	# starting g-code
	# f = open(fname+'.gcode', "w")
	longstring = '%\n' # first line of g-code
	longstring += ('G92\tX0\tY0\n') #set xy coordinates to 0
	longstring += ('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0
	# longstring += ('G1\t'+en+' +{0}] ;ramp\n\n'.format(ramp)) #ramp


	# skirt
	if skirt_i == 'on':
	
		xskirt,yskirt = skirt_c(sdist,side_l)
	
		longstring += ('M63 P'+e_num+' Q10000 E'+str(e_val*10)+'\n') #open valve
		for i in range(0,np.size(xskirt)):
			skirt = 'G1\tX{0}\tY{1}\n'.format(xskirt[i],yskirt[i])
			longstring += (skirt)
		longstring += ('M63 P'+e_num+' Q10000 E0\n') #close valve
		longstring += ('\n') #empty line
	else:
		pass

	# main blocks	  # sample line G1 X4.8 Y1.5 '+en+' + 0.00038 * #<_hw_jogpot>/511]
	h= np.shape(x)[0] # array height
	w= np.shape(x)[1] # array width
	g = 3 #first direction of rotation

	if shape == 'cylinder': # if shape is a circle, draw circles
		for j in range(0,h):
			longstring += ('M63 P'+e_num+' Q10000 E'+str(e_val*10)+'\n') #valve
			for i in range(0,w):
				if i % 2 == 0:
					vrstica = 'G1\tX{0}\tY{1}\n'.format(x[j,i],y[j,i])
				else:
					vrstica = 'G{3}\tX{0}\tY{1}\tR{2}\n'.format(x[j,i],y[j,i],side_l/2,g)
					if g == 3: # switch G2/3 direction
						g = 2
					else:
						g = 3
				longstring += (vrstica)
			longstring += ('M63 P'+e_num+' Q10000 E0\n') #valve
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			longstring += (zline)
			if g == 3: # switch G2/3 direction
				g = 2
			else:
				g = 3
			if j<h-1:
				jump = 'G{3}\tX{0}\tY{1}\tR{2}\tF1600\n'.format(x[j+1,0],y[j+1,0],side_l/2,g) #take FIRST xy elements of NEXT BLOCK
				longstring += (jump)
				longstring += ('G1\tF{0}\n'.format(feedrate))
			else:
				pass
	else: # draw squares
		for j in range(0,h):
			longstring += ('M63 P'+e_num+' Q10000 E'+str(e_val*10)+'\n') #valve
			for i in range(0,w):
				vrstica = 'G1\tX{0}\tY{1}\n'.format(x[j,i],y[j,i])
				longstring += (vrstica)
			longstring += ('M63 P'+e_num+' Q10000 E0\n') #valve
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			longstring += (zline)

	### end g-code
	# longstring += ('G1\t'+en+' -{0}] ;retract\n'.format(ramp)) #retract
	longstring += ('G1\tZ[#<_z> +{0}] ;go to safe height\n'.format(zsafe)) #go to safe height
	longstring += ('G1\tX{0}\tY{1} ;go to next xy position\n'.format(side_l+5,0)) #go to next xy position
	longstring += ('%')
	
	### write to file
	# f = open(fname+'.gcode', "w")
	# f.write(longstring)
	# f.close()
	return longstring

	
def piston(fname,x,y,n,d,shape,side_l,layer_h,layer_n,dist_ext,skirt_i,sdist,feedrate,zsafe,ramp,flow,e_num):

	#### CALCULATE EXTRUSION "A" and reshape to x/y formats
	aflat = d/10*dist_ext 
	a = np.reshape(aflat,np.shape(x)) #reshape to x/y formats
	a = np.round(a,decimals=6)
	en = 'A[#<_a>'
	if e_num == '2':
		en = 'B[#<_b>'
	elif e_num == '6':
		en = 'C[#<_c>'
	
	# starting g-code
	longstring = '%\n' # first line of g-code
	longstring += ('G92\tX0\tY0\n') #set xy coordinates to 0
	longstring += ('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0
	longstring += ('G1\t'+en+' +{0}] ;ramp\n\n'.format(ramp)) #ramp
	
	if skirt_i == 'on':

		### CALCULATE SKIRT
		xskirt,yskirt = skirt_c(sdist,side_l)

		askirt = np.full((1,4),(side_l+sdist)/10*dist_ext)
		askirt = np.append([0],np.ravel(askirt),axis=0)
		askirt = np.append(np.ravel(askirt),[0],axis=0)

		# skirt
		for i in range(0,np.size(xskirt)):
			skirt = ('G1\tX{0}\tY{1}\t'+en+' +{2}]\n').format(xskirt[i],yskirt[i],askirt[i])
			longstring += (skirt)
		longstring += ('\n') #empty line
	else:
		pass

	# main blocks	  # sample line G1 X4.8 Y1.5 '+en+' + 0.00038 * #<_hw_jogpot>/511]
	h= np.shape(x)[0] # array height
	w= np.shape(x)[1] # array width
	g = 3 #first direction of rotation

	if shape == 'cylinder': # if shape is a circle, draw circles
		for j in range(0,h):
			for i in range(0,w):
				if i % 2 == 0:
					vrstica = ('G1\tX{0}\tY{1}\t'+en+' +{2}').format(x[j,i],y[j,i],a[j,i])+flow+']\n'
				else:
					vrstica = ('G{4}\tX{0}\tY{1}\tR{3}\t'+en+' +{2}').format(x[j,i],y[j,i],a[j,i],side_l/2,g)+flow+']\n'
					if g == 3: # switch G2/3 direction
						g = 2
					else:
						g = 3
				longstring += (vrstica)
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			longstring += (zline)
			if g == 3: # switch G2/3 direction
				g = 2
			else:
				g = 3
			if j<h-1:
				jump = 'G{3}\tX{0}\tY{1}\tR{2}\tF1600\n'.format(x[j+1,0],y[j+1,0],side_l/2,g) #take FIRST xy elements of NEXT BLOCK
				longstring += (jump)
				longstring += ('G1\tF{0}\n'.format(feedrate))
			else:
				pass
	else: # draw squares
		for j in range(0,h):
			for i in range(0,w):
				vrstica = ('G1\tX{0}\tY{1}\t'+en+' +{2}').format(x[j,i],y[j,i],a[j,i])+flow+']\n'
				longstring += (vrstica)
			zline = '\nG1\tZ[#<_z> +{0}]\n\n'.format(layer_h)
			longstring += (zline)

	### end g-code
	longstring += (('G1\t'+en+' -{0}] ;retract\n').format(ramp)) #retract
	longstring += ('G1\tZ[#<_z> +{0}] ;go to safe height\n'.format(zsafe)) #go to safe height
	longstring += ('G1\tX{0}\tY{1} ;go to next xy position\n'.format(side_l+5,0)) #go to next xy position
	longstring += ('%')
	
	### write to file
	# f = open(fname+'.gcode', "w")
	# f.write(longstring)
	# f.close()
	return longstring
	


###### EXECUTE G-CODE GENERATOR
'''
x,y,n,d = coordinates()

if skirt_i == "y":
	xskirt,yskirt = skirt_c()
else:
	pass

if drive == "m":
	piston()
else:
	pneumatic()
'''
# seq = open(fname+'.gcode', "r")
# text = seq.read()
# print(text)