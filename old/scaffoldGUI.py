#
#  Developed 2020 by Boštjan Vihar (bostjan AT irnas DOT eu) and Luka Banović (banovic AT irnas DOT eu)
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

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QFileDialog
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap


import numpy as np
from scaffoldGEN import *


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

		self.setMinimumSize(QSize(800, 380))	
		self.setWindowTitle("Vitaprint scaffold generator") 

		
		self.img = QLabel(self) # schematic
		self.img.setPixmap(QPixmap("schematic.png"))
		self.img.setScaledContents(True)
		self.img.move(280, 45)
		self.img.resize(500, 240)


		### SCAFFOLD SHAPE
		self.shape = QLabel(self) # Select scaffold shape
		self.shape.setText('Scaffold shape:')
		self.shape.move(20,20)
		self.shape.resize(135,20)
		
		self.shape_state = QLabel(self) # Current scaffold shape STATE
		self.shape_state.setText('cuboid') # default value
		self.shape_state.move(180,18)
		
		self.shape_i = QComboBox(self) # Drop-down menu scaffold shape
		self.shape_i.addItem('cuboid')
		self.shape_i.addItem('cylinder')
		self.shape_i.move(180,20)
		self.shape_i.resize(100, 20)
		
		self.shape_i.activated[str].connect(self.shape_choice) # call function which returns the selected shape
		
		### EXTRUSION DRIVE
		self.extrusion = QLabel(self) # Select extrusion drive
		self.extrusion.setText('Extrusion mechanism:')
		self.extrusion.move(20, 50)
		self.extrusion.resize(135, 20)
		
		self.extrusion_state = QLabel(self) # Current scaffold shape STATE
		self.extrusion_state.setText('mechanical') # default value
		self.extrusion_state.move(180,48)
		
		self.extrusion_i = QComboBox(self)
		self.extrusion_i.addItem('mechanical')
		self.extrusion_i.addItem('pneumatic')
		self.extrusion_i.move(180,50)
		self.extrusion_i.resize(100, 20)
		
		self.extrusion_i.activated[str].connect(self.extr_choice) # call function which returns the selected extrusion drive

		self.E = QLabel(self) # Extrusion rate
		self.E.setText('Extrusion rate [mm/10mm]:') #only works if mechanical
		self.E.move(25, 73)
		self.E.resize(135, 20)
		
		self.E_i = QLineEdit(self)
		self.E_i.setText('0.2')
		self.E_i.move(180, 73)
		self.E_i.resize(100, 20)
		
		self.retramp = QLabel(self) # Extrusion rate
		self.retramp.setText('Ramp/retraction [mm]:') #only works if mechanical
		self.retramp.move(25, 95)
		self.retramp.resize(135, 20)
		
		self.ramp_i = QLineEdit(self)
		self.ramp_i.setText('0.05')
		self.ramp_i.move(180, 95)
		self.ramp_i.resize(100, 20)
				
		self.flowc = QLabel(self) # Flow control
		self.flowc.setText('Flow control:') #only works if mechanical
		self.flowc.move(25, 110)
		self.flow_s = 'off'
		
		self.flowc_i = QCheckBox(self)
		self.flowc_i.stateChanged.connect(self.flowstate)
		self.flowc_i.move(180,110)


		### SIZE
		self.diameter = QLabel(self)
		self.diameter.setText('Side length/diameter [mm]:')
		self.diameter.move(20, 140)
		self.diameter.resize(135, 20)
		
		self.diameter_i = QLineEdit(self)
		self.diameter_i.setText('10')
		self.diameter_i.move(180, 140)
		self.diameter_i.resize(100, 20)
		
		
		### N OF BARS
		self.nbar = QLabel(self)
		self.nbar.setText('Number of bars:')
		self.nbar.move(20, 165)
		
		self.nbar_i = QLineEdit(self)
		self.nbar_i.setText('7')
		self.nbar_i.move(180, 170)
		self.nbar_i.resize(100, 20)
				
		
		### N-LAYERS
		self.nlay = QLabel(self)
		self.nlay.setText('Number of layers:')
		self.nlay.move(20, 195)
		
		self.nlay_i = QLineEdit(self)
		self.nlay_i.setText('5')
		self.nlay_i.move(180, 200)
		self.nlay_i.resize(100, 20)
		
		
		### LAYER HEIGHT
		self.lh = QLabel(self)
		self.lh.setText('Layer height [mm]:')
		self.lh.move(20, 225)
		
		self.lh_i = QLineEdit(self)
		self.lh_i.setText('0.2')
		self.lh_i.move(180, 230)
		self.lh_i.resize(100, 20)
		
		
		### FEEDRATE
		self.feed = QLabel(self)
		self.feed.setText('Feedrate [mm/min]:')
		self.feed.move(20, 255)
		
		self.feed_i = QLineEdit(self)
		self.feed_i.setText('500')
		self.feed_i.move(180, 260)
		self.feed_i.resize(100, 20)
		

		### SKIRT
		self.skirt = QLabel(self) # Flow control
		self.skirt.setText('Skirt:') #only works if mechanical
		self.skirt.move(20, 285)
		self.skirt_s = 'on'
		
		self.skirt_i = QCheckBox(self)
		self.skirt_i.setChecked(True)
		self.skirt_i.stateChanged.connect(self.skirtyn)
		self.skirt_i.move(180,285)
		
		self.sdist = QLabel(self) # Flow control
		self.sdist.setText('Skirt distance [mm]:') #only works if mechanical
		self.sdist.move(25, 305)
		# self.sdist_s = 'on'
		
		self.sdist_i = QLineEdit(self)
		self.sdist_i.setText('2')
		self.sdist_i.move(180,310)		
		self.sdist_i.resize(100, 20)
		

		### GENERATE BUTTON
		genbut = QPushButton('Generate!', self)
		genbut.setStyleSheet("background-color: green; color: white")
		genbut.clicked.connect(self.clickMethod)
		genbut.resize(100, 20)
		genbut.move(400,300)
		
		clbut = QPushButton('close', self)
		clbut.clicked.connect(self.close_app)
		clbut.resize(100,20)
		clbut.move(510,300)
		
		
		### FILE SAVING
		self.save_to_file = QLabel(self) # Select scaffold shape
		self.save_to_file.setText('Save to file:')
		self.save_to_file.move(20,340)
		self.save_to_file.resize(135,20)
		self.save_s = 'off'
		
		self.save_i = QCheckBox(self)
		self.save_i.setChecked(False)
		self.save_i.stateChanged.connect(self.saveyn)
		self.save_i.move(180,336)
		
		self.browse = QPushButton('Choose Directory', self)
		self.browse.clicked.connect(self.browse_dir)
		self.browse.resize(100, 20)
		self.browse.move(200,340)
		self.browse_i = 'local'
		self.browse.hide()
		
		
	### GENERATING THE SCAFFOLD!!!! #######################################################
	def clickMethod(self,state):
		print('Scaffold shape: ' + self.shape_state.text())
		print('Extrusion mechanism: ' + self.extrusion_state.text())
		if self.extrusion_state.text() == 'mechanical':
			print('Extrusion rate: ' + self.E_i.text() + 'mm/10mm of path')
			print('Flow control: ' + self.flow_s)
		else:
			pass
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
		layer_n = float(self.nlay_i.text())
		layer_h = float(self.lh_i.text())
		feedrate = float(self.feed_i.text())
		shape = self.shape_state.text()
		drive = self.extrusion_state.text()
		if drive == "mechanical":
			dist_ext = float(self.E_i.text())
			ramp = float(self.ramp_i.text())
			flow = self.flow_s
			if flow == 'on':
				flow = '* #<_hw_jogpot>/511'
			else:
				flow = ''

		zsafe = 2 
		skirt_in = self.skirt_s
		if skirt_in == "on":
			sdist_in = float(self.sdist_i.text())
		else:
			sdist_in = "off"
			
		saving = self.save_s # state of file saving
			


		### GENERATE FILENAME
		if drive == "mechanical":
			fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_a'+str(round(dist_ext*100))+'e-2'
		else:
			fname = str(round(side_l))+'x'+str(round(side_l))+'mm_'+shape+'_bar'+str(int(bar_n))+'_h'+str(round(layer_h*10))+'e-1_pneum'
		
		
		### EXECUTE G-CODE GENERATOR
		x,y,n,d = coordinates(side_l,bar_n,shape,layer_n)

		if drive == "mechanical":
			longstring = piston(fname,x,y,n,d,shape,side_l,layer_h,layer_n,dist_ext,skirt_in,sdist_in,feedrate,zsafe,ramp,flow)
		else:
			longstring = pneumatic(fname,x,y,n,d,shape,side_l,layer_h,layer_n,skirt_in,sdist_in,feedrate,zsafe)
		
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
			# gcode.open()

			gc.collect()			
			self.close()

		
	#######################################################################################
	
	def close_app(self):
		print('G-code generator closed')
		self.close()

		
	def shape_choice(self,text):
		self.shape_state.setText(text)
		
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
		else:
			self.E.show()
			self.E_i.show()
			self.flowc.show()
			self.flowc_i.show()
			self.retramp.show()
			self.ramp_i.show()
			
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
		else:
			save_s = 'off'
			self.browse.hide()
			
		self.save_s = save_s
			
	def browse_dir(self):
		browse_i = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		self.browse_i = browse_i


def start():
	app = QtWidgets.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()
	app.quit()

if __name__ == "__main__":
	start()
