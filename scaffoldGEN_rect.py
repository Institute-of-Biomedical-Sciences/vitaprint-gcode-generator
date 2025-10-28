#
#  Developed 2020 by Jernej Vajda (jernej.vajda1 AT um DOT si)
#  Compatible with PlanetCNC TNG version: 2020.06.18
#

import os
import numpy as np

#--- - filament v x-smeri

# |
# | - filament v y-smeri
# |

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

decimalplaces_n = 3

def coordinatesRect(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val):
	if nbars_x % 2 == 1 and nbars_y % 2 == 1:
		x_skirt, y_skirt, x_cons, y_cons, layer_info = xoyo(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val)
	elif nbars_x % 2 == 1 and nbars_y % 2 == 0:
		x_skirt, y_skirt, x_cons, y_cons, layer_info = xoye(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val)
	elif nbars_x % 2 == 0 and nbars_y % 2 == 1:
		x_skirt, y_skirt, x_cons, y_cons, layer_info = xeyo(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val)
	elif nbars_x % 2 == 0 and nbars_y % 2 == 0:
		x_skirt, y_skirt, x_cons, y_cons, layer_info = xeye(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val)
	
	if drive == 'pneumatic':
		longstring = pneumatic_f(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, x_skirt, y_skirt, x_cons, y_cons, layer_info, dist_ext, ramp, flow, e_val)
	else:
		longstring = mechanical_f(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, x_skirt, y_skirt, x_cons, y_cons, layer_info, dist_ext, ramp, flow, e_val)
	
	return longstring

def pneumatic_f(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, x_skirt, y_skirt, x_cons, y_cons, layer_info, dist_ext, ramp, flow, e_val):
	
	longstring = ''
	longstring += '%\n;Set X0Y0.\n'
	longstring += 'G92\tX0\tY0\n\n' #set xy coordinates to 0
	longstring += ';Go to Z0 and set feedrate.\n'
	longstring += 'G1\tZ0\tF{0}\n\n'.format(feedrate) #go to Z0 and set feedrate
	
	if skirt_in == "on":
		longstring += ';Code for skirt.\n'
		longstring += 'M63\tP{0}\tQ10000\tE{1}\n'.format(int(e_num),float(e_val*10))
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[0],y_skirt[0])
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[1],y_skirt[1])
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[2],y_skirt[2])
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[3],y_skirt[3])
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[4],y_skirt[4])
		longstring += ';Go to starting position.\n'
		longstring += 'G1\tX0\tY0\n\n' #go to X0 Y0
	
	currentCon = 0
	
	for a in range(0,layer_n):
		longstring += 'M63\tP{0}\tQ10000\tE{1}\n'.format(int(e_num),float(e_val*10))
		
		for b in range(currentCon, currentCon + layer_info[a]):
			longstring += 'G1\tX{0}\tY{1}\n'.format(x_cons[b],y_cons[b])
		currentCon += layer_info[a]
		longstring += 'M63\tP{0}\tQ10000\tE0\n\n'.format(int(e_num))
		longstring += 'G91\nG1\tZ{0}\nG90\n\n'.format(layer_h)
	
	longstring += 'G91\nG1\tZ{0}\nG90\n\n'.format(zsafe)
	longstring += 'G1\tX{0}\tY{1}\n%'.format(side_x+5,side_y+5)
	
	return(longstring)

def mechanical_f(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, x_skirt, y_skirt, x_cons, y_cons, layer_info, dist_ext, ramp, flow, e_val):
	
	if e_num == '1':
		e_label_u = 'A'
		e_label_l = 'a'
	elif e_num == '2':
		e_label_u = 'B'
		e_label_l = 'b'
	else:
		e_label_u = 'C'
		e_label_l = 'c'
	
	longstring = ''
	longstring += '%\n;Set X0Y0.\n'
	longstring += 'G92\tX0\tY0\n\n' #set xy coordinates to 0
	longstring += ';Go to Z0 and set feedrate.\n'
	longstring += 'G1\tZ0\tF{0}\n\n'.format(feedrate) #go to Z0 and set feedrate
	
	def euclid_dist(x2, y2, x1, y1):
		dist = np.sqrt((x2-x1)**2+(y2-y1)**2)
		dist = round(dist, 4)
		dist = 100000*dist
		dist = int(dist)
		return dist
	
	if skirt_in == "on":
		longstring += ';Code for skirt.\n'
		longstring += 'G1\tX{0}\tY{1}\n'.format(x_skirt[0],y_skirt[0])
		longstring += 'G1\tX{0}\tY{1}\t{2}[#<_{3}> +{4}]\n'.format(x_skirt[1],y_skirt[1],e_label_u,e_label_l,dist_ext*euclid_dist(x_skirt[1], y_skirt[1], x_skirt[0], y_skirt[0])/1000000)
		longstring += 'G1\tX{0}\tY{1}\t{2}[#<_{3}> +{4}]\n'.format(x_skirt[2],y_skirt[2],e_label_u,e_label_l,dist_ext*euclid_dist(x_skirt[2], y_skirt[2], x_skirt[1], y_skirt[1])/1000000)
		longstring += 'G1\tX{0}\tY{1}\t{2}[#<_{3}> +{4}]\n'.format(x_skirt[3],y_skirt[3],e_label_u,e_label_l,dist_ext*euclid_dist(x_skirt[3], y_skirt[3], x_skirt[2], y_skirt[2])/1000000)
		longstring += 'G1\tX{0}\tY{1}\t{2}[#<_{3}> +{4}]\n'.format(x_skirt[4],y_skirt[4],e_label_u,e_label_l,dist_ext*euclid_dist(x_skirt[4], y_skirt[4], x_skirt[3], y_skirt[3])/1000000)
		longstring += ';Go to starting position.\n'
		longstring += 'G1\tX0\tY0\t{0}[#<_{1}> +{2}]\n\n'.format(e_label_u,e_label_l,dist_ext*euclid_dist(0, 0, x_skirt[4], y_skirt[4])/1000000) #go to X0 Y0
	
	currentCon = 0
	
	for a in range(0,layer_n):
		for b in range(currentCon, currentCon + layer_info[a]):
			longstring += 'G1\tX{0}\tY{1}\t{2}[#<_{3}> +{4}'.format(x_cons[b],y_cons[b],e_label_u,e_label_l,dist_ext*euclid_dist(x_cons[b], y_cons[b], x_cons[b-1], y_cons[b-1])/1000000) + flow + ']\n'
		currentCon += layer_info[a]
		longstring += '\n'
		longstring += 'G91\nG1\tZ{0}\nG90\n\n'.format(layer_h)
	
	longstring += 'G1\t{0}[#<_{1}> -{2}] ;retract\n\n'.format(e_label_u,e_label_l,ramp) #retract
	longstring += 'G91\nG1\tZ{0}\nG90\n\n'.format(zsafe)
	longstring += 'G1\tX{0}\tY{1}\n%'.format(side_x+5,side_y+5)
	
	return(longstring)
	
def xoyo(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val):
	x = []
	y = []
	
	x_skirt = []
	y_skirt = []
	
	x_cons = []
	y_cons = []
	
	layer_info = []
	
	xInc = side_x/(nbars_y-1) #x increment; mora biti nbars_y
	yInc = side_y/(nbars_x-1) #y increment; mora biti nbars_x
	
	for i in range(0,nbars_y):
		x.append(round(i*xInc,decimalplaces_n))
	for j in range(0,nbars_x):
		y.append(round(j*yInc,decimalplaces_n))
	
	xLen = len(x)
	yLen = len(y)
	n = 0
	
	if skirt_in == "on":
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)
	
	while n < layer_n:
		if n < layer_n:
			for k in range(0,int((2*nbars_x-2)/4)): #filamenti v smeri x
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+2])
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			for l in range(0,int((2*nbars_y-2)/4)): #filamenti v smeri y
				x_cons.append(x[xLen-1-2*l])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*l-1])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*l-1])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-2*l-2])
				y_cons.append(y[yLen-1])
			x_cons.append(x[0])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
	
	# print(x_cons)
	# print(y_cons)
	# print(len(x_cons))
	# print(len(y_cons))
	# print(layer_info)
	# print(x)
	# print(y)
	
	x_cons.append(0)
	y_cons.append(0)
	
	
	return x_skirt, y_skirt, x_cons, y_cons, layer_info


def xeyo(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val):
	x = []
	y = []
	
	x_skirt = []
	y_skirt = []
	
	x_cons = []
	y_cons = []
	
	layer_info = []

	xInc = side_x/(nbars_y-1) #x increment
	yInc = side_y/(nbars_x-1) #y increment
	
	for i in range(0,nbars_y):
		x.append(round(i*xInc,decimalplaces_n))
	for j in range(0,nbars_x):
		y.append(round(j*yInc,decimalplaces_n))
	
	xLen = len(x)
	yLen = len(y)
	n = 0
	
	longstring ='\n;Set X0Y0.\n'
	longstring += ('G92\tX0\tY0\n\n') #set xy coordinates to 0
	longstring += (';Go to Z0 and set feedrate.\n')
	longstring += ('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0 and set feedrate
	
	if skirt_in == "on":
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)

	while n < layer_n:
		if n < layer_n:
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			x_cons.append(x[xLen-1])
			y_cons.append(y[1])
			for k in range(0,int((2*nbars_x)/4-1)): #filamenti v smeri x
				x_cons.append(x[0])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+2])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+2])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+3])
			x_cons.append(x[0])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			for l in range(0,int((2*nbars_y-2)/4)): #filamenti v smeri y
				x_cons.append(x[2*l])
				y_cons.append(y[0])
				x_cons.append(x[2*l+1])
				y_cons.append(y[0])
				x_cons.append(x[2*l+1])
				y_cons.append(y[yLen-1])
				x_cons.append(x[2*l+2])
				y_cons.append(y[yLen-1])
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[0])
			y_cons.append(y[0])
			x_cons.append(x[0])
			y_cons.append(y[1])
			for m in range(0,int((2*nbars_x)/4-1)): #filamenti v smeri x
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*m+1])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*m+2])
				x_cons.append(x[0])
				y_cons.append(y[2*m+2])
				x_cons.append(x[0])
				y_cons.append(y[2*m+3])
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			for o in range(0,int((2*nbars_y-2)/4)): #filamenti v smeri y
				x_cons.append(x[xLen-1-2*o])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-1])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-1])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-2*o-2])
				y_cons.append(y[yLen-1])
			x_cons.append(x[0])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
	
	# print(x_cons)
	# print(y_cons)
	# print(len(x_cons))
	# print(len(y_cons))
	# print(layer_info)
	# print(x)
	# print(y)
	
	x_cons.append(0)
	y_cons.append(0)
	
	return x_skirt, y_skirt, x_cons, y_cons, layer_info

def xoye(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val):
	x = []
	y = []
	
	x_skirt = []
	y_skirt = []
	
	x_cons = []
	y_cons = []
	
	layer_info = []

	xInc = side_x/(nbars_y-1) #x increment
	yInc = side_y/(nbars_x-1) #y increment
	
	for i in range(0,nbars_y):
		x.append(round(i*xInc,decimalplaces_n))
	for j in range(0,nbars_x):
		y.append(round(j*yInc,decimalplaces_n))
	
	xLen = len(x)
	yLen = len(y)
	n = 0
	
	longstring ='\n;Set X0Y0.\n'
	longstring += ('G92\tX0\tY0\n\n') #set xy coordinates to 0
	longstring += (';Go to Z0 and set feedrate.\n')
	longstring += ('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0 and set feedrate
	
	if skirt_in == "on":
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)

	while n < layer_n:
		if n < layer_n:
			for k in range(0,int((2*nbars_x-2)/4)): #filamenti v smeri x
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+2])
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			x_cons.append(x[xLen-1-1])
			y_cons.append(y[0])
			for l in range(0,int((2*nbars_y)/4-1)): #filamenti v smeri y
				x_cons.append(x[xLen-1-1-2*l])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-1-2*l-1])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-1-2*l-1])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-1-2*l-2])
				y_cons.append(y[0])
			x_cons.append(x[0])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			for m in range(0,int((2*nbars_x-2)/4)): #filamenti v smeri x
				x_cons.append(x[xLen-1])
				y_cons.append(y[yLen-1-2*m])
				x_cons.append(x[xLen-1])
				y_cons.append(y[yLen-1-2*m-1])
				x_cons.append(x[0])
				y_cons.append(y[yLen-1-2*m-1])
				x_cons.append(x[0])
				y_cons.append(y[yLen-1-2*m-2])
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			x_cons.append(x[xLen-1-1])
			y_cons.append(y[yLen-1])
			for o in range(0,int((2*nbars_y)/4-1)): #filamenti v smeri y
				x_cons.append(x[xLen-1-2*o-1])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-2])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-2])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-2*o-3])
				y_cons.append(y[yLen-1])
			x_cons.append(x[0])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
	
	# print(x_cons)
	# print(y_cons)
	# print(len(x_cons))
	# print(len(y_cons))
	# print(layer_info)
	# print(x)
	# print(y)
	
	x_cons.append(0)
	y_cons.append(0)
	
	return x_skirt, y_skirt, x_cons, y_cons, layer_info
	
def xeye(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow, e_val):
	x = []
	y = []
	
	x_skirt = []
	y_skirt = []
	
	x_cons = []
	y_cons = []
	
	layer_info = []

	xInc = side_x/(nbars_y-1) #x increment
	yInc = side_y/(nbars_x-1) #y increment
	
	for i in range(0,nbars_y):
		x.append(round(i*xInc,decimalplaces_n))
	for j in range(0,nbars_x):
		y.append(round(j*yInc,decimalplaces_n))
	
	xLen = len(x)
	yLen = len(y)
	n = 0
	
	longstring ='\n;Set X0Y0.\n'
	longstring += ('G92\tX0\tY0\n\n') #set xy coordinates to 0
	longstring += (';Go to Z0 and set feedrate.\n')
	longstring += ('G1\tZ0\tF{0}\n\n'.format(feedrate)) #go to Z0 and set feedrate
	
	if skirt_in == "on":
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(-sdist_in)
		x_skirt.append(x[xLen-1]+sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(y[yLen-1]+sdist_in)
		x_skirt.append(-sdist_in)
		y_skirt.append(-sdist_in)

	while n < layer_n:
		if n < layer_n: 
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			x_cons.append(x[xLen-1])
			y_cons.append(y[1])
			for k in range(0,int((2*nbars_x)/4-1)): #filamenti v smeri x
				x_cons.append(x[0])
				y_cons.append(y[2*k+1])
				x_cons.append(x[0])
				y_cons.append(y[2*k+2])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+2])
				x_cons.append(x[xLen-1])
				y_cons.append(y[2*k+3])
			x_cons.append(x[0])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[0])
			y_cons.append(y[0])
			x_cons.append(x[1])
			y_cons.append(y[0])
			for l in range(0,int((2*nbars_y)/4-1)): #filamenti v smeri y
				x_cons.append(x[2*l+1])
				y_cons.append(y[yLen-1])
				x_cons.append(x[2*l+2])
				y_cons.append(y[yLen-1])
				x_cons.append(x[2*l+2])
				y_cons.append(y[0])
				x_cons.append(x[2*l+3])
				y_cons.append(y[0])
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[0])
			y_cons.append(y[yLen-1])
			x_cons.append(x[0])
			y_cons.append(y[yLen-1-1])
			for m in range(0,int((2*nbars_x)/4-1)): #filamenti v smeri x
				x_cons.append(x[xLen-1])
				y_cons.append(y[yLen-1-2*m-1])
				x_cons.append(x[xLen-1])
				y_cons.append(y[yLen-1-2*m-2])
				x_cons.append(x[0])
				y_cons.append(y[yLen-1-2*m-2])
				x_cons.append(x[0])
				y_cons.append(y[yLen-1-2*m-3])
			x_cons.append(x[xLen-1])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_x-1)
			
			n += 1
		else:
			break
		
		if n < layer_n:
			x_cons.append(x[xLen-1])
			y_cons.append(y[yLen-1])
			x_cons.append(x[xLen-1-1])
			y_cons.append(y[yLen-1])
			for o in range(0,int((2*nbars_y)/4-1)): #filamenti v smeri y
				x_cons.append(x[xLen-1-2*o-1])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-2])
				y_cons.append(y[0])
				x_cons.append(x[xLen-1-2*o-2])
				y_cons.append(y[yLen-1])
				x_cons.append(x[xLen-1-2*o-3])
				y_cons.append(y[yLen-1])
			x_cons.append(x[0])
			y_cons.append(y[0])
			
			layer_info.append(2*nbars_y-1)
			
			n += 1
		else:
			break
	
	# print(x_cons)
	# print(y_cons)
	# print(len(x_cons))
	# print(len(y_cons))
	# print(layer_info)
	# print(x)
	# print(y)
	
	x_cons.append(0)
	y_cons.append(0)
	
	return x_skirt, y_skirt, x_cons, y_cons, layer_info