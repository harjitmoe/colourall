"""Chip viewer and widget.

In the lower left corner of the main ColourAll window, you will see two
ChipWidgets, one for the selected colour and one for the nearest colour.  The
selected colour is the actual RGB value expressed as an X11 #COLOR name. The
nearest colour is the named colour from the X11 database that is closest to the
selected colour in 3D space.  There may be other colours equally close, but the
nearest one is the first one found.

Clicking on the nearest colour chip selects that named colour.

The ChipViewer class includes the entire lower left quandrant; i.e. both the
selected and nearest ChipWidgets.
"""

from types import StringType
from Tkinter import *
import ColourDB


class ChipWidget:
    _WIDTH = 150
    _HEIGHT = 80

    def __init__(self,
                 master = None,
                 width  = _WIDTH,
                 height = _HEIGHT,
                 text   = 'Colour',
                 initialcolour = 'blue',
                 presscmd   = None,
                 releasecmd = None):
        # create the text label
        self.__label = Label(master, text=text)
        self.__label.grid(row=0, column=0)
        # create the colour chip, implemented as a frame
        self.__chip = Frame(master, relief=RAISED, borderwidth=2,
                            width=width,
                            height=height,
                            background=initialcolour)
        self.__chip.grid(row=1, column=0)
        # create the colour name
        self.__namevar = StringVar()
        self.__namevar.set(initialcolour)
        self.__name = Entry(master, textvariable=self.__namevar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=2, column=0)
        # create the message area
        self.__msgvar = StringVar()
        self.__name = Entry(master, textvariable=self.__msgvar,
                            relief=FLAT, justify=CENTER, state=DISABLED,
                            font=self.__label['font'])
        self.__name.grid(row=3, column=0)
        # set bindings
        if presscmd:
            self.__chip.bind('<ButtonPress-1>', presscmd)
        if releasecmd:
            self.__chip.bind('<ButtonRelease-1>', releasecmd)

    def set_colour(self, colour):
        self.__chip.config(background=colour)

    def get_colour(self):
        return self.__chip['background']

    def set_name(self, colourname):
        self.__namevar.set(colourname)

    def set_message(self, message):
        self.__msgvar.set(message)

    def press(self):
        self.__chip.configure(relief=SUNKEN)

    def release(self):
        self.__chip.configure(relief=RAISED)



class ChipViewer:
    def __init__(self, switchboard, master=None, sa=0):
        try:
            Label(master)
        except TclError:
            sa=2
            master=master.master
        if sa:
            root = self.__root = Toplevel(master, class_='ColourAll')
            root.title(ADDTOVIEW)
            root.iconname(ADDTOVIEW)
            master=root
            self.deiconify=lambda self=self,s=switchboard,m=master:self.__init__(s,m,0)
            if sa!=2:
                return
        self.__sb = switchboard
        self.__frame = Frame(master, relief=RAISED, borderwidth=1)
        self.__frame.grid(row=3, column=0, ipadx=5, sticky='NSEW')
        # create the chip that will display the currently selected colour
        # exactly
        self.__sframe = Frame(self.__frame)
        self.__sframe.grid(row=0, column=0)
        self.__selected = ChipWidget(self.__sframe, text='Selected')
        # create the chip that will display the nearest real X11 colour
        # database colour name
        self.__nframe = Frame(self.__frame)
        self.__nframe.grid(row=0, column=1)
        self.__nearest = ChipWidget(self.__nframe, text='Nearest',
                                    presscmd = self.__buttonpress,
                                    releasecmd = self.__buttonrelease)
        
        self.update_yourself(switchboard._Switchboard__red,switchboard._Switchboard__green,switchboard._Switchboard__blue)

    def update_yourself(self, red, green, blue):
        # Selected always shows the #rrggbb name of the colour, nearest always
        # shows the name of the nearest colour in the database.  BAW: should
        # an exact match be indicated in some way?
        #
        # Always use the #rrggbb style to actually set the colour, since we may
        # not be using X colour names (e.g. "web-safe" names)
        colourdb = self.__sb.colourdb()
        rgbtuple = (red, green, blue)
        rrggbb = ColourDB.triplet_to_rrggbb(rgbtuple)
        # find the nearest
        nearest = colourdb.nearest(red, green, blue)
        nearest_tuple = colourdb.find_byname(nearest)
        nearest_rrggbb = ColourDB.triplet_to_rrggbb(nearest_tuple)
        self.__selected.set_colour(rrggbb)
        self.__nearest.set_colour(nearest_rrggbb)
        # set the name and messages areas
        self.__selected.set_name(rrggbb)
        if rrggbb == nearest_rrggbb:
            self.__selected.set_message(nearest)
        else:
            self.__selected.set_message('')
        self.__nearest.set_name(nearest_rrggbb)
        self.__nearest.set_message(nearest)

    def __buttonpress(self, event=None):
        self.__nearest.press()

    def __buttonrelease(self, event=None):
        self.__nearest.release()
        rrggbb = self.__nearest.get_colour()
        red, green, blue = ColourDB.rrggbb_to_triplet(rrggbb)
        self.__sb.update_views(red, green, blue)
