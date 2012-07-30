"""GotoViewer class.

This class implements a "go to colour window"

This is better than doing it through the (long) list and picks up (the
now many) aliases too!
"""

from Tkinter import *
import ColourDB
from tkSimpleDialog import askstring

ADDTOVIEW = 'Go to colour...'

class GotoViewer:
	def __init__(self, switchboard, master=None, sa=0):
		#This is supposed to create a withdrawn widget
		#Irrelevant
		self.__sb=switchboard
		self.__m=master

	def update_yourself(self, red, green, blue):
		pass

	def save_options(self, optiondb):
		pass

	def colourdb_changed(self, colourdb):
		pass
	
	def deiconify(self):
		name=""
		if self.__m:
			while not name:
				name=askstring("Enter colour...", "Please enter a colour string to look up", parent=self.__m)
				if name==None:
					return
			if name[0]=="#":
				r,g,b=ColourDB.rrggbb_to_triplet(name)
			else:
				r,g,b=self.__sb.colourdb().find_byname(name)
			self.__sb.update_views(r,g,b)
	
	def withdraw(self):
		#Nice one!
		pass
