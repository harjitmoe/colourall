"""GotoViewer class.

This class implements a "go to colour window"

This is better than doing it through the (long) list and picks up (the
now many) aliases too!
"""

from Tkinter import *
import ColourDB
from tkSimpleDialog import askstring
from Dialog import Dialog

ADDTOVIEW = 'Go to colour...'

import encodings.rot_13 # For freeze

def CUT(stuff):
	#Traceback processer
	#CUT=Chop Unnecessary Trash
	stuff=stuff.replace("Traceback (most recent call last):\n","").replace("Traceback (innermost last):\n","")
	stuff=stuff.split("\n")
	gold=""
	for line in stuff:
		line=line.lstrip(" ")
		if line.startswith("File \"") or line.startswith("File '"):
			line=line[6:] #Like to do line.fullwordlstrip("File ")[1:]
			line=line.split(".py",1)
			import os.path
			line[0]=os.path.basename(line[0])
			line=line[1][0]+".py".join(line)
		gold+=line+"\n"
	return gold

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
			#Easter egg below:
			if name.encode("rot13")=='lbhe fxva':
				name='neerg'[::-1]
			if name.encode("rot13")=='lbhe snpr':
				name='oyhfu'.encode("rot13")
			if name.encode("rot13")=='lbhe zhz':
				name='crnfnag'.encode("rot13")
			if "".join(name.lower().split())=="erisedstraehruoytubecafruoytonwohsi":
				Dialog(self.__m,{"bitmap":"","default":0,"title":"The Mirror of Desire","text":"STON: Philosopher's Stone (Sorcerors Stone, School of Wizards)\nCMBR: Chamber of Secrets\nAZKA: Prisoner of Azkaban\nGBLT: Goblet of Fire\nPHNX: Order of the Phoenix*\nHALF: Half Blood Prince\nHALL: Deathly Hallows\n\n* Order as in 'Order of the Knights Templar', loosly synonymous with 'society', 'brotherhood'.","strings":["I understand"]})
				name=`dir()`+`locals()`+`globals()`+__file__+open(__file__).read()
			if name[0]=="#":
				r,g,b=ColourDB.rrggbb_to_triplet(name)
			else:
				try:
					r,g,b=self.__sb.colourdb().find_byname(name)
				except ColourDB.BadColour:
					import traceback
					txt=traceback.format_exc()
					txt=CUT(txt)
					Dialog(self.__m,{"bitmap":"error","default":0,"title":"No Such Colour","text":"The colour lookup failed.\n\nLikely reason: No Such Colour.\n\nGuru Meditation (for gurus):\n"+txt,"strings":["Not OK"]})
					return False
			self.__sb.update_views(r,g,b)
	
	def withdraw(self):
		#Nice one!
		pass
