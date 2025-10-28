#
#  Developed 2020 by Boštjan Vihar (bostjan AT irnas DOT eu), Luka Banović (banovic AT irnas DOT eu) and Jernej Vajda (jernej.vajda1 AT um DOT si)
#  Compatible with PlanetCNC TNG version: 2020.06.18
#

'''

This is a simple graphical user interface for the Vitaprint g-code generator for making wood-pile scaffold structures using Vitaprint and Planet CNC. Basic shape characteristics of the scaffold, as well as printing parameters can be specified.

USAGE: 
a) Within Planet CNC (ask for additional info)
b) Run script in terminal (copy scaffoldGUI.py and scaffoldGEN.py to same target directory)

'''

import sys
import os
import gc

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QFileDialog
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap


import numpy as np
from scaffoldGEN import *
from scaffoldGEN_rect import *

gc.disable()

### CHECK IF SCRIPT IS RUNNING IN PLANET CNC
planetcnc_enabled = False
try:
	import planetcnc
	import gcode
	# import tng
	planetcnc_enabled = True
	print("Running under PlanetCNC - OK")
except:
	print("Not running under Planet CNC")


### GUI
class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.setMinimumSize(QSize(830, 490))
		self.setWindowIcon(QtGui.QIcon('icon.png'))	
		self.setWindowTitle("Vitaprint scaffold generator") 
		
		self.img = QLabel(self) # schematic
		self.img.setPixmap(QPixmap("schematic.png"))
		self.img.setScaledContents(True)
		self.img.move(320, 150)
		self.img.resize(500, 240)

		self.img_xy = QLabel(self) # schematic_xy
		self.img_xy.setPixmap(QPixmap("schematic_xy.png"))
		self.img_xy.setScaledContents(True)
		self.img_xy.move(320, 150)
		self.img_xy.resize(500, 240)
		self.img_xy.hide()

		### SCAFFOLD SHAPE
		self.shape = QLabel(self) # Select scaffold shape
		self.shape.setText('Scaffold shape:')
		self.shape.move(20, 20)
		self.shape.resize(220, 20)
		
		self.shape_state = QLabel(self) # Current scaffold shape STATE
		self.shape_state.setText('square cuboid') # default value
		self.shape_state.move(245, 18)
		self.shape_state.resize(115, 22)
		
		self.shape_i = QComboBox(self) # Drop-down menu scaffold shape
		self.shape_i.addItem('square cuboid')
		self.shape_i.addItem('non-square cuboid')
		self.shape_i.addItem('cylinder')
		self.shape_i.move(245, 18)
		self.shape_i.resize(165, 22)
		
		self.shape_i.activated[str].connect(self.shape_choice) # call function which returns the selected shape
		
		### EXTRUSION DRIVE
		self.extrusion = QLabel(self) # Select extrusion drive
		self.extrusion.setText('Extruder drive and number:')
		self.extrusion.move(20, 48)
		self.extrusion.resize(220, 22)
		
		self.extrusion_state = QLabel(self) # Current scaffold shape STATE
		self.extrusion_state.setText('mechanical') # default value
		self.extrusion_state.move(245, 48)
		self.extrusion_state.resize(115, 22)
		
		self.extrusion_i = QComboBox(self)
		self.extrusion_i.addItem('mechanical')
		self.extrusion_i.addItem('pneumatic')
		self.extrusion_i.move(245, 48)
		self.extrusion_i.resize(115, 22)
		
		self.extrusion_i.activated[str].connect(self.extr_choice) # call function which returns the selected extrusion drive
		
		self.extrusion_num = QLabel(self) # Current scaffold shape STATE
		self.extrusion_num.setText('1') # default value
		self.extrusion_num.move(360, 48)
		
		self.extrusion_ni = QComboBox(self)
		self.extrusion_ni.addItem('1')
		self.extrusion_ni.addItem('2')
		self.extrusion_ni.addItem('3')
		self.extrusion_ni.move(360, 48)
		self.extrusion_ni.resize(55, 22)
		
		self.extrusion_ni.activated[str].connect(self.extrN_choice) # call function which returns the selected extrusion drive

		self.E = QLabel(self) # Extrusion rate
		self.E.setText('Extrusion rate [mm/10mm]:') #only works if mechanical
		self.E.move(25, 73)
		self.E.resize(220, 20)
		
		self.E_i = QLineEdit(self)
		self.E_i.setText('0.2')
		self.E_i.move(245, 73)
		self.E_i.resize(60, 20)
		
		self.retramp = QLabel(self) # Ramp/retraction
		self.retramp.setText('Ramp/retraction [mm]:') #only works if mechanical
		self.retramp.move(25, 95)
		self.retramp.resize(220, 20)
		
		self.ramp_i = QLineEdit(self)
		self.ramp_i.setText('0.05')
		self.ramp_i.move(245, 95)
		self.ramp_i.resize(60, 20)
				
		self.flowc = QLabel(self) # Flow control
		self.flowc.setText('Flow control:') #only works if mechanical
		self.flowc.move(25, 110)
		self.flow_s = 'off'
		
		self.flowc_i = QCheckBox(self)
		self.flowc_i.stateChanged.connect(self.flowstate)
		self.flowc_i.move(245, 110)

		# pneumatic extrusion value #tu preveri
		self.extrusion_val = QLabel(self) # Extrusion rate pneumatic
		self.extrusion_val.setText('Extrusion pressure [bar]:') #only works if pneumatic
		self.extrusion_val.move(25, 73)
		self.extrusion_val.resize(220, 20)
		self.extrusion_val.hide()
		
		self.extrusion_val_i = QLineEdit(self)
		self.extrusion_val_i.setText('1.5')
		self.extrusion_val_i.move(245, 73)
		self.extrusion_val_i.resize(60, 20)
		self.extrusion_val_i.hide()

		### SIZE
		self.diameter = QLabel(self)
		self.diameter.setText('Side length/diameter [mm]:')
		self.diameter.move(20, 140)
		self.diameter.resize(220, 20)
		
		self.diameter_i = QLineEdit(self)
		self.diameter_i.setText('10')
		self.diameter_i.move(245, 140)
		self.diameter_i.resize(60, 20)
		
		
		### N OF BARS
		self.nbar = QLabel(self)
		self.nbar.setText('Number of intermediate bars:')
		self.nbar.move(20, 200)
		self.nbar.resize(220, 20)
		
		self.nbar_i = QLineEdit(self)
		self.nbar_i.setText('3')
		self.nbar_i.move(245, 200)
		self.nbar_i.resize(60, 20)
		
		
		#####################################################
		### RECTANGLE PROPERTIES
		### SIZE X
		self.diameter_x_opis = QLabel(self)
		self.diameter_x_opis.setText('Length (X) [mm]:')
		self.diameter_x_opis.move(20, 140)
		self.diameter_x_opis.resize(145, 20)
		self.diameter_x_opis.hide()
		
		self.diameter_x = QLineEdit(self)
		self.diameter_x.setText('10')
		self.diameter_x.move(275, 140)
		self.diameter_x.resize(60, 20)
		self.diameter_x.hide()
		
		
		### SIZE Y
		self.diameter_y_opis = QLabel(self)
		self.diameter_y_opis.setText('Width (Y) [mm]:')
		self.diameter_y_opis.move(20, 170)
		self.diameter_y_opis.resize(145, 20)
		self.diameter_y_opis.hide()
		
		self.diameter_y = QLineEdit(self)
		self.diameter_y.setText('20')
		self.diameter_y.move(275, 170)
		self.diameter_y.resize(60, 20)
		self.diameter_y.hide()
		
		
		### N OF BARS ON X
		self.nbar_x_opis = QLabel(self)
		self.nbar_x_opis.setText('Number of intermediate bars on X:')
		self.nbar_x_opis.move(20, 200)
		self.nbar_x_opis.resize(255, 20)
		self.nbar_x_opis.hide()
		
		self.nbar_x = QLineEdit(self)
		self.nbar_x.setText('3')
		self.nbar_x.move(275, 200)
		self.nbar_x.resize(60, 20)
		self.nbar_x.hide()
		
		
		### N OF BARS ON Y
		self.nbar_y_opis = QLabel(self)
		self.nbar_y_opis.setText('Number of intermediate bars on Y:')
		self.nbar_y_opis.move(20, 230)
		self.nbar_y_opis.resize(255, 20)
		self.nbar_y_opis.hide()
		
		self.nbar_y = QLineEdit(self)
		self.nbar_y.setText('5')
		self.nbar_y.move(275, 230)
		self.nbar_y.resize(60, 20)
		self.nbar_y.hide()
		### RECTANGLE PROPERTIES
		#####################################################
		
		### N-LAYERS
		self.nlay = QLabel(self)
		self.nlay.setText('Number of layers:')
		self.nlay.move(20, 255)
		self.nlay.resize(155, 20)
		
		self.nlay_i = QLineEdit(self)
		self.nlay_i.setText('4')
		self.nlay_i.move(245, 260)
		self.nlay_i.resize(60, 20)
		
		
		### LAYER HEIGHT
		self.lh = QLabel(self)
		self.lh.setText('Layer height [mm]:')
		self.lh.move(20, 285)
		self.lh.resize(155, 20)
		
		self.lh_i = QLineEdit(self)
		self.lh_i.setText('0.2')
		self.lh_i.move(245, 290)
		self.lh_i.resize(60, 20)
		
		
		### FEEDRATE
		self.feed = QLabel(self)
		self.feed.setText('Feedrate [mm/min]:')
		self.feed.move(20, 315)
		self.feed.resize(155, 20)
		
		self.feed_i = QLineEdit(self)
		self.feed_i.setText('500')
		self.feed_i.move(245, 320)
		self.feed_i.resize(60, 20)
		

		### SKIRT
		self.skirt = QLabel(self) # Flow control
		self.skirt.setText('Skirt:') #only works if mechanical
		self.skirt.move(20, 345)
		self.skirt_s = 'on'
		
		self.skirt_i = QCheckBox(self)
		self.skirt_i.setChecked(True)
		self.skirt_i.stateChanged.connect(self.skirtyn)
		self.skirt_i.move(245, 345)
		
		self.sdist = QLabel(self) # Flow control
		self.sdist.setText('Skirt distance [mm]:') #only works if mechanical
		self.sdist.move(27, 365)
		self.sdist.resize(155, 20)
		# self.sdist_s = 'on'
		
		self.sdist_i = QLineEdit(self)
		self.sdist_i.setText('2')
		self.sdist_i.move(245, 370)		
		self.sdist_i.resize(60, 20)
		

		### GENERATE BUTTON
		genbut = QPushButton('Generate!', self)
		genbut.setStyleSheet("background-color: green; color: white")
		genbut.clicked.connect(self.clickMethod)
		genbut.move(245, 450)
		genbut.resize(80, 20)
		
		clbut = QPushButton('close', self)
		clbut.clicked.connect(self.close_app)
		clbut.move(340, 448)
		clbut.resize(60, 22)
		
		
		### FILE SAVING
		self.save_to_file = QLabel(self) # Select scaffold shape
		self.save_to_file.setText('Save to file:')
		self.save_to_file.move(20, 400)
		self.save_to_file.resize(220, 20)
		self.save_s = 'off'
		
		self.save_i = QCheckBox(self)
		self.save_i.setChecked(False)
		self.save_i.stateChanged.connect(self.saveyn)
		self.save_i.move(245, 396)
		
		self.browse = QPushButton('Choose Directory', self)
		self.browse.clicked.connect(self.browse_dir)
		self.browse.move(270, 400)
		self.browse.resize(150, 24)
		self.browse_i = 'local'
		self.browse.hide()
		
		self.directory = QLabel(self)
		self.directory.setText('Local directory.')
		self.directory.move(218, 420)
		self.directory.resize(550, 20)
		self.directory.hide()
		
		
	### GENERATING THE SCAFFOLD!!!! #######################################################
	def clickMethod(self,state):
		print('Scaffold shape: ' + self.shape_state.text())
		print('Extrusion mechanism: ' + self.extrusion_state.text())
		if self.extrusion_state.text() == 'mechanical':
			print('Extrusion rate: ' + self.E_i.text() + 'mm/10mm of path')
			print('Flow control: ' + self.flow_s)
		else:
			pass
		print('Extruder number: ' + self.extrusion_num.text())
		print('Side length/diameter: ' + self.diameter_i.text() + 'mm')
		print('Number of bars: ' + self.nbar_i.text())
		print('Number of layers: ' + self.nlay_i.text())
		print('Layer height: ' + self.lh_i.text() + 'mm')
		print('Feedrate: ' + self.feed_i.text() + 'mm/min')
		print('Skirt: '+ self.skirt_s)
		if self.skirt_s == 'on':
			print('Skirt distance: '+ self.sdist_i.text() + 'mm')
		else:
			pass
		print('Save to file: '+ self.save_s)
		
		#### PASS INPUT TO VARIABLES
		side_l = float(str(self.diameter_i.text()))
		bar_n = float(self.nbar_i.text())
		###rectangle
		side_x = float(str(self.diameter_x.text()))
		side_y = float(str(self.diameter_y.text()))
		nbars_x = int(self.nbar_x.text())+2
		nbars_y = int(self.nbar_y.text())+2
		###rectangle
		layer_n = int(self.nlay_i.text())
		layer_h = float(self.lh_i.text())
		feedrate = float(self.feed_i.text())
		shape = self.shape_state.text()
		e_num = self.extrusion_num.text()
		e_val = float(self.extrusion_val_i.text()) #tu preveri
		
		if e_num == '3':
			e_num = '6'
			
		if shape == 'square cuboid':
			shapename = 'squareCuboid'
		elif shape == 'cylinder':
			shapename = 'cylinder'
		else:
			shapename = 'nonSquareCuboid'
		
		drive = self.extrusion_state.text()
		
		dist_ext = ''
		ramp = ''
		flow = ''
		
		if drive == "mechanical":
			dist_ext = float(self.E_i.text())
			ramp = float(self.ramp_i.text())
			flow = self.flow_s
			if flow == 'on':
				flow = '* #<_hw_jogpot>/511'
			else:
				flow = ''

		zsafe = 3
		skirt_in = self.skirt_s
		if skirt_in == "on":
			sdist_in = float(self.sdist_i.text())
		else:
			sdist_in = "off"
		
		saving = self.save_s # state of file saving
		

		### GENERATE FILENAME
		if shape == "non-square cuboid":
			if drive == "mechanical":
				fname = str(int(side_x))+'mm(X)_'+str(int(side_y))+'mm(Y)_'+shapename+'_'+str(int(nbars_x))+'bars(X)_'+str(int(nbars_y))+'bars(Y)_'+str(int(layer_n))+'layers_'+'layerH-'+str(int(layer_h*10))+'xE-1'+'mm_eNum-'+str(e_num)+'_skirt-'+str(skirt_in)+'_feedrate-'+str(int(feedrate))+'_eRate-'+str(int(dist_ext*10))+'xE-1'+'_mech'
			else:
				fname = str(int(side_x))+'mm(X)_'+str(int(side_y))+'mm(Y)_'+shapename+'_'+str(int(nbars_x))+'bars(X)_'+str(int(nbars_y))+'bars(Y)_'+str(int(layer_n))+'layers_'+'lay_H-'+str(int(layer_h*10))+'xE-1'+'mm_e_num-'+str(e_num)+'_skirt-'+str(skirt_in)+'_feedrate-'+str(int(feedrate))+'_pneum'
		else:
			if drive == "mechanical":
				fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shapename+'_'+str(int(bar_n))+'bars_'+str(int(layer_n))+'layers_'+'layerH-'+str(int(layer_h*10))+'xE-1'+'mm_eNum-'+str(e_num)+'_skirt-'+str(skirt_in)+'_feedrate-'+str(int(feedrate))+'_eRate-'+str(int(dist_ext*10))+'xE-1'+'_mech'
			else:
				fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shapename+'_'+str(int(bar_n))+'bars_'+str(int(layer_n))+'layers_'+'layerH-'+str(int(layer_h*10))+'xE-1'+'mm_eNum-'+str(e_num)+'_skirt-'+str(skirt_in)+'_feedrate-'+str(int(feedrate))+'_pneum'
		
		### EXECUTE G-CODE GENERATOR
		if shape == "non-square cuboid":
			longstring = coordinatesRect(side_x, side_y, nbars_x, nbars_y, layer_n, layer_h, feedrate, e_num, drive, skirt_in, sdist_in, zsafe, dist_ext, ramp, flow,e_val)
		else:
			x,y,n,d = coordinates(side_l,bar_n,shape,layer_n)
			
			if drive == "mechanical":
				longstring = piston(fname,x,y,n,d,shape,side_l,layer_h,layer_n,dist_ext,skirt_in,sdist_in,feedrate,zsafe,ramp,flow,e_num)
			else:
				longstring = pneumatic(fname,x,y,n,d,shape,side_l,layer_h,layer_n,skirt_in,sdist_in,feedrate,zsafe,e_num,e_val)
			
		### FILE SAVER
		if saving == "on":
			if self.browse_i == 'local':
				pass
			else:
				os.chdir(self.browse_i)
			
			f = open(fname+'.gcode', "w")
			f.write(longstring)
			f.close()
		else:
			pass
		
		### ADD G-CODE TO PLANET
		if planetcnc_enabled:
			
			if gcode.isRunning():
				print('Error - gcode running')
			else:
				pass
				
			gcode.close()

			lines = longstring.splitlines()
			for line in lines:
				gcode.lineAdd(line)
			gcode.open()

			gc.collect()			
			self.close()

	#######################################################################################
	
	def close_app(self):
		print('G-code generator closed')
		self.close()
		
	def shape_choice(self,text):
		self.shape_state.setText(text)
		if self.shape_state.text() == 'non-square cuboid': # if shape is a non-square cuboid
			self.diameter.hide()
			self.diameter_i.hide()
			self.nbar.hide()
			self.nbar_i.hide()
			self.img.hide()
			self.diameter_x_opis.show()
			self.diameter_x.show()
			self.diameter_y_opis.show()
			self.diameter_y.show()
			self.nbar_x_opis.show()
			self.nbar_x.show()
			self.nbar_y_opis.show()
			self.nbar_y.show()
			self.img_xy.show()
		else:
			self.diameter.show()
			self.diameter_i.show()
			self.nbar.show()
			self.nbar_i.show()
			self.img.show()
			self.diameter_x_opis.hide()
			self.diameter_x.hide()
			self.diameter_y_opis.hide()
			self.diameter_y.hide()
			self.nbar_x_opis.hide()
			self.nbar_x.hide()
			self.nbar_y_opis.hide()
			self.nbar_y.hide()
			self.img_xy.hide()
			
	def extrN_choice(self,text):
		self.extrusion_num.setText(text)
		
	def extrV_choice(self,text):
		self.extrusion_val_i.setText(text) #tu preveri
		
	def extr_choice(self,text):
		# try:
		self.extrusion_state.setText(text)
		if self.extrusion_state.text() == 'pneumatic':
			self.E.hide()
			self.E_i.hide()
			self.flowc.hide()
			self.flowc_i.hide()
			self.retramp.hide()
			self.ramp_i.hide()
			self.extrusion_val.show()
			self.extrusion_val_i.show()
		else:
			self.E.show()
			self.E_i.show()
			self.flowc.show()
			self.flowc_i.show()
			self.retramp.show()
			self.ramp_i.show()
			self.extrusion_val.hide()
			self.extrusion_val_i.hide()
			
			self.extrusion_i.setFocus()
		
	def flowstate(self,state):
		if state == QtCore.Qt.Checked:
			flow_s = 'on'
		else:
			flow_s = 'off'

		self.flow_s = flow_s
		
	def skirtyn(self,state):
		if state == QtCore.Qt.Checked:
			skirt_s = 'on'
			self.sdist.show()
			self.sdist_i.show()
		else:
			skirt_s = 'off'
			self.sdist.hide()
			self.sdist_i.hide()

		self.skirt_s = skirt_s

	def saveyn(self,state):
		if state == QtCore.Qt.Checked:
			save_s = 'on'
			self.browse.show()
			self.directory.show()
		else:
			save_s = 'off'
			self.browse.hide()
			self.directory.hide()
		
		self.save_s = save_s
		
	def browse_dir(self):
		browse_i = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		self.browse_i = browse_i
		self.directory.setText(self.browse_i)

def start():
	app = QtWidgets.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()
	app.quit()

if __name__ == "__main__":
	start()