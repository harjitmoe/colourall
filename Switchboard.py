"""Switchboard class.

This class is used to coordinate updates among all Viewers.  Every Viewer must
conform to the following interface:

    - it must include a method called update_yourself() which takes three
      arguments; the red, green, and blue values of the selected colour.

    - When a Viewer selects a colour and wishes to update all other Views, it
      should call update_views() on the Switchboard object.  Note that the
      Viewer typically does *not* update itself before calling update_views(),
      since this would cause it to get updated twice.

Optionally, Viewers can also implement:

    - save_options() which takes an optiondb (a dictionary).  Store into this
      dictionary any values the Viewer wants to save in the persistent
      colorall.ini (which is actually a pickle;).  This should be 8.3.

    - withdraw() which takes no arguments.  This is called when ColourAll is
      unmapped.  This is strongly recommended.

    - colourdb_changed() which takes a single argument, an instance of
      ColourDB.  This is called whenever the colour name database is changed and
      gives a chance for the Viewers to do something on those events.  See
      ListViewer for details.

External Viewers are found dynamically.  Viewer modules should have names such
as FooViewer.py.  If such a named module has a module global variable called
ADDTOVIEW and this variable is true, the Viewer will be added dynamically to
the `View' menu.  ADDTOVIEW contains a string which is used as the menu item
to display the Viewer (one kludge: if the string contains a `%', this is used
to indicate that the next character will get an underline in the menu,
otherwise the first character is underlined).

Note that viewers for compilation into EXE are found STATICALLY by 
ColourAllWidget.py

FooViewer.py should contain a class called FooViewer, and its constructor
should take two arguments, an instance of Switchboard, and optionally a Tk
master window.

"""

import sys
import os
from types import DictType
import pickle

myfile=os.path.abspath(sys.argv[0])
mydir=os.path.dirname(myfile)
config=os.path.join(mydir,"colorall.ini")

class Switchboard:
    def __init__(self, initfile):
        self.__initfile = initfile
        self.__colourdb = None
        self.__optiondb = {}
        self.__views = []
        self.__red = 0
        self.__green = 0
        self.__blue = 0
        self.__canceled = 0
        self.__optiondb.update({
            #These options make life easier by far...
            "HEXTYPE":1,
            "UPWHILETYPE":1,
            "UPWHILEDRAG":1,
	})
	if os.path.exists(config):
		self.__optiondb.update(pickle.load(open(config,"rU")))
        self.__optiondb.update({
            #...and these are required due to the non-X palette
            'TEXTBG':"white",
            'TEXTFG':"black",
            'TEXT_IBG':"black",
            'TEXT_SBG':"navy",
            'TEXT_SFG':"white",
        })

    def add_view(self, view):
        self.__views.append(view)

    def update_views(self, red, green, blue):
        if red>255:red=255
        if green>255:green=255
        if blue>255:blue=255
        self.__red = red
        self.__green = green
        self.__blue = blue
        for v in self.__views:
            v.update_yourself(red, green, blue)
	self.save_views()

    def update_views_current(self):
        self.update_views(self.__red, self.__green, self.__blue)

    def current_rgb(self):
        return self.__red, self.__green, self.__blue

    def colourdb(self):
        return self.__colourdb

    def set_colourdb(self, colourdb):
        self.__colourdb = colourdb
        for v in self.__views:
            if hasattr(v, 'colourdb_changed'):
                v.colourdb_changed(colourdb)
        self.update_views_current()

    def optiondb(self):
        return self.__optiondb

    def withdraw_views(self):
        self.save_views()
        for v in self.__views:
            if hasattr(v, 'withdraw'):
                v.withdraw()

    def save_views(self):
        for v in self.__views:
	    if hasattr(v, 'save_options'):
		v.save_options(self.__optiondb)
	pickle.dump(self.__optiondb,open(config,"w"),0)

    def canceled(self, flag=1):
        self.__canceled = flag

    def canceled_p(self):
        return self.__canceled
