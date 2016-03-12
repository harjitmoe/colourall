"""ListViewer class.

This class implements an input/output view on the colour model.  It lists every
unique colour (e.g. unique r/g/b value) found in the colour database.  Each
colour is shown by small swatch and primary colour name.  Some colours have
aliases -- more than one name for the same r/g/b value.  These aliases are
displayed in the small listbox at the bottom of the screen.

Clicking on a colour name or swatch selects that colour and updates all other
windows.  When a colour is selected in a different viewer, the colour list is
scrolled to the selected colour and it is highlighted.  If the selected colour
is an r/g/b value without a name, no scrolling occurs.

You can turn off Update On Click if all you want to see is the alias for a
given name, without selecting the colour.
"""

from Tkinter import *
import ColourDB

# Import *object-oriented* canvas shape interface
from Canvas import *	#You think this is obsolete? Think again! ~THH

#ADDTOVIEW = 'Colour %List Window...'

class ListViewer:
    def __init__(self, switchboard, master=None, sa=0, mode="Luma"):
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        self.__lastbox = None
        self.__lastlabel = None
        self.__lastview = None
        self.__dontcenter = 0
        # GUI
        try:
            Label(master)
        except TclError:
            sa=2
            master=master.master
        if sa:
            root = self.__root = Toplevel(master, class_='ColourAll')
            root.protocol('WM_DELETE_WINDOW', self.withdraw)
            root.title('ColourAll Colour List')
            root.iconname('ColourAll Colour List')
            root.bind('<Alt-q>', self.__quit)
            root.bind('<Alt-Q>', self.__quit)
            root.bind('<Alt-w>', self.withdraw)
            root.bind('<Alt-W>', self.withdraw)
            self.deiconify=lambda self=self,s=switchboard,m=root:self.__init__(s,m,0)
            if sa!=2:
                return
        else:
            root = Frame(master, relief=RAISED, borderwidth=1)
            root.grid(row=1, column=3, rowspan=3, sticky='NSEW')
            if not hasattr(root,"withdraw"):
                root.withdraw=lambda:None
        self.__root=root
        #
        # create the canvas which holds everything, and its scrollbar
        #
        frame = self.__frame = Frame(root)
        frame.pack()
        canvas = self.__canvas = Canvas(frame, width=160, height=211,
                                        borderwidth=2, relief=SUNKEN)
        self.__scrollbar = Scrollbar(frame)
        self.__scrollbar.pack(fill=Y, side=RIGHT)
        canvas.pack(fill=BOTH, expand=1)
        canvas.configure(yscrollcommand=(self.__scrollbar, 'set'))
        self.__scrollbar.configure(command=(canvas, 'yview'))
        self.__contents=[]
        #self.__populate()
        #
        # radios
        frame=Frame(root)
        frame.pack(expand=1, fill=BOTH)
        self.__radiotxt=["Alphabet","Luma","Chroma","Red","Green","Blue"]
        self.__radios = []
        self.__which = StringVar()
        self.__which.set(mode)
        print "GOT",mode
        for radio,txt in zip(range(len(self.__radiotxt)),self.__radiotxt):
            r = Radiobutton(frame, variable=self.__which,
                            value=txt,
                            text=txt,
                            command=self.__set_sortmode)
            r.grid(row=radio%3, column=radio//3, sticky=W)
            self.__radios.append(r)
        self.__set_sortmode()
        #
        # Update on click
        self.__uoc = BooleanVar()
        self.__uoc.set(optiondb.get('UPONCLICK', 1))
        self.__uocbtn = Checkbutton(root,
                                    text='Update on Click',
                                    variable=self.__uoc,
                                    command=self.__toggleupdate)
        self.__uocbtn.pack(expand=1, fill=BOTH)
        #
        # alias list
        self.__alabel = Label(root, text='Aliases:')
        self.__alabel.pack()
        self.__aliases = Listbox(root, height=5,
                                 selectmode=BROWSE)
        self.__scrollbar2 = Scrollbar(root)
        self.__scrollbar2.pack(fill=Y, side=RIGHT)
        self.__aliases.pack(expand=1, fill=BOTH)
        self.__aliases.configure(yscrollcommand=(self.__scrollbar2, 'set'))
        self.__scrollbar2.configure(command=(self.__aliases, 'yview'))

    def __set_sortmode(self, event=None):
        self.mode = self.__which.get()
        print "USING",self.mode
        self.__populate()

    def __populate(self):
        #
        # create all the buttons
        colourdb = self.__sb.colourdb()
        canvas = self.__canvas
        for i in self.__contents:
            i.delete()
        self.__contents=[]
        row = 0
        widest = 0
        bboxes = self.__bboxes = []
        self.__contents.append(Rectangle(canvas, 0, 0,
                               160, 300,
                               outline='',
                               fill="#FFFFFF"))
        for name in colourdb.unique_names(self.mode):
            #Whitewash
            self.__contents.append(Rectangle(canvas, 0, row*20+3,
                                   160, row*20 + 30,
                                   outline='',
                                   fill="#FFFFFF"))
            
            #Preview
            exactcolour = ColourDB.triplet_to_rrggbb(colourdb.find_byname(name))
            previd = Rectangle(canvas, 5, row*20 + 5,
                               20, row*20 + 20,
                               fill=exactcolour,
                               tags=("V"+exactcolour, 'Vall'))
            self.__contents.append(previd)
            
            #Label
            textid = CanvasText(canvas, 25, row*20 + 13,
                                text=name,
                                anchor=W,
                                tags=("T"+exactcolour, 'Tall'))
            self.__contents.append(textid)
            
            #Selection Rectangle
            boxid = Rectangle(canvas, 0, row*20+4,
                              160, row*20 + 22,
                              outline='',
                              tags=(exactcolour, 'all'))
            textid.tkraise()
            previd.tkraise()
            self.__contents.append(boxid)
            bboxes.append(boxid.id) #The handle not the Python object
            
            #Onclick Behaviour
            canvas.bind('<ButtonRelease>', self.__onrelease)
            row = row + 1
        
        canvheight = (row-1)*20 + 25
        canvas.config(scrollregion=(0, 0, 150, canvheight))
        #print self.__contents

    def __onrelease(self, event=None):
        canvas = self.__canvas
        
        # find the current box
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        
        ids = canvas.find_overlapping(x, y, x, y)
        for boxid in ids:
            if boxid in self.__bboxes:
                break
        else:
            return
        
        tags = self.__canvas.gettags(boxid)
        for t in tags:
            if t[0] == '#':
                break
        else:
            return
        
        red, green, blue = ColourDB.rrggbb_to_triplet(t)
        self.__dontcenter = 1
        if self.__uoc.get():
            self.__sb.update_views(red, green, blue)
        else:
            self.update_yourself(red, green, blue)
            self.__red, self.__green, self.__blue = red, green, blue

    def __toggleupdate(self, event=None):
        if self.__uoc.get():
            self.__sb.update_views(self.__red, self.__green, self.__blue)

    def __quit(self, event=None):
        self.__root.quit()

    def withdraw(self, event=None):
        self.__root.withdraw()

    def deiconify(self, event=None):
        self.__root.deiconify()

    def update_yourself(self, red, green, blue):
        canvas = self.__canvas
        # turn off the last box
        if self.__lastbox:
            canvas.itemconfigure(self.__lastbox, fill="")
        if self.__lastlabel:
            canvas.itemconfigure(self.__lastlabel, fill="#000000")
        if self.__lastview:
            canvas.itemconfigure(self.__lastview, outline="#000000")
        # turn on the current box
        colourtag = ColourDB.triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colourtag, fill='#102080')
        self.__lastbox = colourtag
        colourlabeltag = "T"+ColourDB.triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colourlabeltag, fill='#FFFFFF')
        self.__lastlabel = colourlabeltag
        colourviewtag = "V"+ColourDB.triplet_to_rrggbb((red, green, blue))
        canvas.itemconfigure(colourviewtag, outline='#FFFFFF')
        self.__lastview = colourviewtag
        # fill the aliases
        self.__aliases.delete(0, END)
        try:
            aliases_ = self.__sb.colourdb().aliases_of(red, green, blue)
            not_alias=[aliases_[0].replace(" ","").lower()]
            aliases=[]
            for try_alias in aliases_:
                if try_alias.replace(" ","").lower() not in not_alias:
                    aliases.append(try_alias)
                    not_alias.append(try_alias.replace(" ","").lower())
        except ColourDB.BadColour:
            self.__aliases.insert(END, '<no matching colour>')
            return
        if not aliases:
            self.__aliases.insert(END, '<no aliases>')
        else:
            for name in aliases:
                self.__aliases.insert(END, name)
        # maybe scroll the canvas so that the item is visible
        if self.__dontcenter:
            self.__dontcenter = 0
        else:
            ig, ig, ig, y1 = canvas.coords(colourtag)
            ig, ig, ig, y2 = canvas.coords(self.__bboxes[-1])
            h = int(canvas['height']) * 0.5
            canvas.yview('moveto', (y1-h) / y2)

    def save_options(self, optiondb):
        optiondb['UPONCLICK'] = self.__uoc.get()

    def colourdb_changed(self, colourdb):
        self.__canvas.delete('all')
        self.__populate()
