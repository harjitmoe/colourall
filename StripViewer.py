"""Strip viewer and related widgets.

The classes in this file implement the StripViewer shown in the top two thirds
of the main ColourAll window.  It consists of three StripWidgets which display
the variations in red, green, and blue respectively of the currently selected
r/g/b colour value.

Each StripWidget shows the colour variations that are reachable by varying an
axis of the currently selected colour.  So for example, if the colour is

  (R,G,B)=(127,163,196)

then the Red variations show colours from (0,163,196) to (255,163,196), the
Green variations show colours from (127,0,196) to (127,255,196), and the Blue
variations show colours from (127,163,0) to (127,163,255).

The selected colour is always visible in all three StripWidgets, and in fact
each StripWidget highlights the selected colour, and has an arrow pointing to
the selected chip, which includes the value along that particular axis.

Clicking on any chip in any StripWidget selects that colour, and updates all
arrows and other windows.  By toggling on Update while dragging, ColourAll will
select the colour under the cursor while you drag it, but be forewarned that
this can be slow.
"""

from Tkinter import *
import ColourDB

# Load this script into the Tcl interpreter and call it in
# StripWidget.set_colour().  This is about as fast as it can be with the
# current _tkinter.c interface, which doesn't support Tcl Objects.
TCLPROC = '''\
proc setcolour {canv colours} {
    set i 1
    foreach c $colours {
        $canv itemconfigure $i -fill $c -outline $c
        incr i
    }
}
'''

# Tcl event types
BTNDOWN = 4
BTNUP = 5
BTNDRAG = 6

SPACE = ' '


def cmy_to_rgb(c,m,y):
	r=(m+y)/2
	g=(c+y)/2
	b=(c+m)/2
	r=255-r
	g=255-g
	b=255-b
	return r,g,b

rgb_to_cmy=cmy_to_rgb #Same matrix, apparantly
def constant(numchips):
    #Go one over then force to 255
    #Not elegant but allows for more elegant numchips
    seq = []
    for i in range(numchips):
        if i==(numchips-1):
            seq.append(255)
        else:
            seq.append((i*256) // (numchips - 1))
    return seq

def constantab(numchips,b_minus_a):
    #Go one over then force to 255
    #Not elegant but allows for more elegant numchips
    step = 256.0 / (numchips - 1)
    start = 0.0
    seq = []
    while numchips > 0:
        seq.append(int(start))
        start = start + step
        numchips = numchips - 1
    seqa=seq[:]
    seqb=seq[:]
    b_minus_a_firsthalf=b_minus_a//2
    b_minus_a_secondhalf=b_minus_a-b_minus_a_firsthalf
    for i in range(len(seqa)):
        seqa[i]=seqa[i]+b_minus_a_firsthalf
        if seqa[i]>255:
            seqa[i]=255
        if seqa[i]<0:
            seqa[i]=0
    for i in range(len(seqb)):
        seqb[i]=seqb[i]-b_minus_a_secondhalf
        if seqb[i]>255:
            seqb[i]=255
        if seqb[i]<0:
            seqb[i]=0
    return seqa,seqb

# red constant, green+blue = cyan variations
def constant_red_generator(numchips, red, green, blue):
    seqa,seqb = constantab(numchips,green-blue)
    return zip( [red] * numchips, seqa, seqb)

# green constant, red+blue = magenta variations
def constant_green_generator(numchips, red, green, blue):
    seqa,seqb = constantab(numchips,red-blue)
    return zip( seqa, [green] * numchips, seqb)

# blue constant, red+green = yellow variations
def constant_blue_generator(numchips, red, green, blue):
    seqa,seqb = constantab(numchips,red-green)
    return zip( seqa, seqb, [blue] * numchips)

# red variations, green+blue = cyan constant
def constant_cyan_generator(numchips, red, green, blue):
    seq = constant(numchips)
    return zip( seq, [green] * numchips, [blue] * numchips)

# green variations, red+blue = magenta constant
def constant_magenta_generator(numchips, red, green, blue):
    seq = constant(numchips)
    return zip( [red] * numchips, seq, [blue] * numchips)

# blue variations, red+green = yellow constant
def constant_yellow_generator(numchips, red, green, blue):
    seq = constant(numchips)
    return zip( [red] * numchips, [green] * numchips, seq)



class LeftArrow:
    _ARROWWIDTH = 30
    _ARROWHEIGHT = 15
    _YOFFSET = 13
    _TEXTYOFFSET = 1
    _TAG = ('leftarrow',)

    def __init__(self, canvas, x):
        self._canvas = canvas
        self.__arrow, self.__text = self._create(x)
        self.move_to(x)

    def _create(self, x):
        arrow = self._canvas.create_line(
            x, self._ARROWHEIGHT + self._YOFFSET,
            x, self._YOFFSET,
            x + self._ARROWWIDTH, self._YOFFSET,
            arrow='first',
            width=3.0,
            tags=self._TAG)
        text = self._canvas.create_text(
            x + self._ARROWWIDTH + 13,
            self._ARROWHEIGHT - self._TEXTYOFFSET,
            tags=self._TAG,
            text='128')
        return arrow, text

    def _x(self):
        coords = self._canvas.coords(self._TAG)
        assert coords
        return coords[0]

    def hidetext(self):
        #self._canvas.itemconfig(self.__text,tags=())
        self.move_text_to(-1000)

    def showtext(self):
        #self._canvas.itemconfig(self.__text,tags=self._TAG)
        self.move_text_back()

    def move_to(self, x):
        deltax = x - self._x()
        self._canvas.move(self._TAG, deltax, 0)
    def move_text_to(self, x):
        deltax = x - self._x()
        self.__last_text_deltax=deltax
        self._canvas.move(self.__text, deltax, 0)
    def move_text_back(self):
        self._canvas.move(self.__text, -self.__last_text_deltax, 0)

    def set_text(self, text):
        self._canvas.itemconfigure(self.__text, text=text)


class RightArrow(LeftArrow):
    _TAG = ('rightarrow',)

    def _create(self, x):
        arrow = self._canvas.create_line(
            x, self._YOFFSET,
            x + self._ARROWWIDTH, self._YOFFSET,
            x + self._ARROWWIDTH, self._ARROWHEIGHT + self._YOFFSET,
            arrow='last',
            width=3.0,
            tags=self._TAG)
        text = self._canvas.create_text(
            x - self._ARROWWIDTH + 15,            # BAW: kludge
            self._ARROWHEIGHT - self._TEXTYOFFSET,
            justify=RIGHT,
            text='128',
            tags=self._TAG)
        return arrow, text

    def _x(self):
        coords = self._canvas.coords(self._TAG)
        assert coords
        return coords[0] + self._ARROWWIDTH



class StripWidget:
    _CHIPHEIGHT = 25
    _CHIPWIDTH = 5
    _NUMCHIPS = 65
    
    def __init__(self, switchboard,
                 master     = None,
                 chipwidth  = _CHIPWIDTH,
                 chipheight = _CHIPHEIGHT,
                 numchips   = _NUMCHIPS,
                 generator  = None,
                 axis       = None,
                 label      = '',
                 uwdvar     = None,
                 hexvar     = None):
        # instance variables
        self.__generator = generator
        self.__axis = axis
        self.__numchips = numchips
        assert self.__axis in (0, 1, 2)
        self.__uwd = uwdvar
        self.__hexp = hexvar
        # the last chip selected
        self.__lastchip = None
        self.__sb = switchboard

        canvaswidth = numchips * (chipwidth + 1)
        canvasheight = chipheight + 43            # BAW: Kludge

        # create the canvas and pack it
        canvas = self.__canvas = Canvas(master,
                                        width=canvaswidth,
                                        height=canvasheight,
##                                        borderwidth=2,
##                                        relief=GROOVE
                                        )

        canvas.pack()
        canvas.bind('<ButtonPress-1>', self.__select_chip)
        canvas.bind('<ButtonRelease-1>', self.__select_chip)
        canvas.bind('<B1-Motion>', self.__select_chip)

        # Load a proc into the Tcl interpreter.  This is used in the
        # set_colour() method to speed up setting the chip colours.
        canvas.tk.eval(TCLPROC)

        # create the colour strip
        chips = self.__chips = []
        x = 1
        y = 30
        tags = ('chip',)
        for c in range(self.__numchips):
            colour = 'grey'
            canvas.create_rectangle(
                x, y, x+chipwidth, y+chipheight,
                fill=colour, outline=colour,
                tags=tags)
            x = x + chipwidth + 1                 # for outline
            chips.append(colour)

        # create the strip label
        self.__label = canvas.create_text(
            3, y + chipheight + 8,
            text=label,
            anchor=W)

        # create the arrow and text item
        chipx = self.__arrow_x(0)
        self.__leftarrow = LeftArrow(canvas, chipx)

        chipx = self.__arrow_x(len(chips) - 1)
        self.__rightarrow = RightArrow(canvas, chipx)

    def __arrow_x(self, chipnum):
        coords = self.__canvas.coords(chipnum+1)
        assert coords
        x0, y0, x1, y1 = coords
        return (x1 + x0) / 2.0

    # Invoked when one of the chips is clicked.  This should just tell the
    # switchboard to set the colour on all the output components
    def __select_chip(self, event=None):
        x = event.x
        y = event.y
        canvas = self.__canvas
        chip = canvas.find_overlapping(x, y, x, y)
        if chip and (1 <= chip[0] <= self.__numchips):
            colour = self.__chips[chip[0]-1]
            red, green, blue = ColourDB.rrggbb_to_triplet(colour)
            etype = int(event.type)
            if (etype == BTNUP or self.__uwd.get()):
                # update everyone
                self.__sb.update_views(red, green, blue)
            else:
                # just track the arrows
                self.__trackarrow(chip[0], (red, green, blue))

    def __trackarrow(self, chip, rgbtuple):
        # invert the last chip
        if self.__lastchip is not None:
            colour = self.__canvas.itemcget(self.__lastchip, 'fill')
            self.__canvas.itemconfigure(self.__lastchip, outline=colour)
        self.__lastchip = chip
        # get the arrow's text
        colouraxis = rgbtuple[self.__axis]
        if self.__hexp.get():
            # hex
            text = hex(colouraxis)
        else:
            # decimal
            text = repr(colouraxis)
        # move the arrow, and set its text
        if colouraxis <= 128:
            # use the left arrow
            self.__leftarrow.set_text(text)
            self.__leftarrow.move_to(self.__arrow_x(chip-1))
            self.__rightarrow.move_to(-100)
        else:
            # use the right arrow
            self.__rightarrow.set_text(text)
            self.__rightarrow.move_to(self.__arrow_x(chip-1))
            self.__leftarrow.move_to(-100)
        # and set the chip's outline
        brightness = ColourDB.triplet_to_brightness(rgbtuple)
        if brightness <= 128:
            outline = 'white'
        else:
            outline = 'black'
        self.__canvas.itemconfigure(chip, outline=outline)
    
    def hidearrow(self): #FIXME misnomer, more like hidetext
        self.__rightarrow.hidetext()
        self.__leftarrow.hidetext()
    def showarrow(self): #FIXME misnomer, more like showtext
        self.__rightarrow.showtext()
        self.__leftarrow.showtext()

    def update_yourself(self, red, green, blue):
        assert self.__generator
        i = 1
        chip = 0
        chips = self.__chips = []
        tk = self.__canvas.tk
        # get the red, green, and blue components for all chips
        for t in self.__generator(self.__numchips, red, green, blue):
            rrggbb = ColourDB.triplet_to_rrggbb(t)
            chips.append(rrggbb)
            tred, tgreen, tblue = t
            if tred <= red and tgreen <= green and tblue <= blue:
                chip = i
            i = i + 1
        # call the raw tcl script
        colours = SPACE.join(chips)
        tk.eval('setcolour %s {%s}' % (self.__canvas._w, colours))
        # move the arrows around
        self.__trackarrow(chip, (red, green, blue))

    def set(self, label, generator):
        self.__canvas.itemconfigure(self.__label, text=label)
        self.__generator = generator


class StripViewer:
    def __init__(self, switchboard, master=None, sa=0):
        try:
            Label(master)
        except TclError:
            sa=2
            master=master.master
        if sa:
            ##root = self.__root = Toplevel(master, class_='ColourAll')
            ##root.title(ADDTOVIEW)
            ##root.iconname(ADDTOVIEW)
            ##master=root
            ##self.deiconify=lambda self=self,s=switchboard,m=master:self.__init__(s,m,0)
            ##if sa!=2:
            ##    return
            self.deiconify=lambda:None
            return
        self.__sb = switchboard
        optiondb = switchboard.optiondb()
        # create a frame inside the master.
        frame = Frame(master, relief=RAISED, borderwidth=1)
        frame.grid(row=1, column=0, columnspan=2, sticky='NSEW')
        # create the options to be used later
        uwd = self.__uwdvar = BooleanVar()
        uwd.set(optiondb.get('UPWHILEDRAG', 0))
        hexp = self.__hexpvar = BooleanVar()
        hexp.set(optiondb.get('HEXSTRIP', 0))
        # create the red, green, blue strips inside their own frame
        frame1 = Frame(frame)
        frame1.pack(expand=YES, fill=BOTH)
        self.__reds = StripWidget(switchboard, frame1,
                                  generator=constant_cyan_generator,
                                  axis=0,
                                  label='Red',
                                  uwdvar=uwd, hexvar=hexp)

        self.__greens = StripWidget(switchboard, frame1,
                                    generator=constant_magenta_generator,
                                    axis=1,
                                    label='Green',
                                    uwdvar=uwd, hexvar=hexp)

        self.__blues = StripWidget(switchboard, frame1,
                                   generator=constant_yellow_generator,
                                   axis=2,
                                   label='Blue',
                                   uwdvar=uwd, hexvar=hexp)

        # create a frame to contain the controls
        frame2 = Frame(frame)
        frame2.pack(expand=YES, fill=BOTH)
        frame2.columnconfigure(0, weight=20)
        frame2.columnconfigure(2, weight=20)

        padx = 8

        # create the black button
        blackbtn = Button(frame2,
                          text='Black',
                          command=self.__toblack)
        blackbtn.grid(row=0, column=0, rowspan=2, sticky=W, padx=padx)

        # create the controls
        uwdbtn = Checkbutton(frame2,
                             text='Update while dragging',
                             variable=uwd)
        uwdbtn.grid(row=0, column=1, sticky=W)
        hexbtn = Checkbutton(frame2,
                             text='Hexadecimal',
                             variable=hexp,
                             command=self.__togglehex)
        hexbtn.grid(row=0, column=2, sticky=W)

        # THH got the below feature working sortof

        frame3=Frame(frame)
        frame3.pack(expand=YES, fill=BOTH)
        gentypevar = self.__gentypevar = IntVar()
        self.__variations = Radiobutton(frame3,
                                        text='Channels',
                                        variable=self.__gentypevar,
                                        value=0,
                                        command=self.__togglegentype)
        self.__variations.grid(row=1, column=1, sticky=W)
        self.__constants = Radiobutton(frame3,
                                       text='Double-Channels (faulty?)',
                                       variable=self.__gentypevar,
                                       value=1,
                                       command=self.__togglegentype)
        self.__constants.grid(row=1, column=2, sticky=W)

        # create the white button
        whitebtn = Button(frame2,
                          text='White',
                          command=self.__towhite)
        whitebtn.grid(row=0, column=3, rowspan=2, sticky=E, padx=padx)
        
        ##self.update_yourself(switchboard._Switchboard__red,switchboard._Switchboard__green,switchboard._Switchboard__blue)

    def update_yourself(self, red, green, blue):
        if hasattr(self,"_StripViewer__reds"):
            self.__reds.update_yourself(red, green, blue)
            self.__greens.update_yourself(red, green, blue)
            self.__blues.update_yourself(red, green, blue)

    def __togglehex(self, event=None):
        red, green, blue = self.__sb.current_rgb()
        self.update_yourself(red, green, blue)

    def __togglegentype(self, event=None):
        which = self.__gentypevar.get()
        if which == 0:
            self.__reds.set(label='Red',
                            generator=constant_cyan_generator)
            self.__reds.showarrow()
            self.__greens.set(label='Green',
                              generator=constant_magenta_generator)
            self.__greens.showarrow()
            self.__blues.set(label='Blue',
                             generator=constant_yellow_generator)
            self.__blues.showarrow()
        elif which == 1:
            self.__reds.set(label='Non-Red',
                            generator=constant_red_generator)
            self.__reds.hidearrow()
            self.__greens.set(label='Non-Green',
                              generator=constant_green_generator)
            self.__greens.hidearrow()
            self.__blues.set(label='Non-Blue',
                             generator=constant_blue_generator)
            self.__blues.hidearrow()
        else:
            assert 0
        self.__sb.update_views_current()

    def __toblack(self, event=None):
        self.__sb.update_views(0, 0, 0)

    def __towhite(self, event=None):
        self.__sb.update_views(255, 255, 255)

    def save_options(self, optiondb):
        optiondb['UPWHILEDRAG'] = self.__uwdvar.get()
        optiondb['HEXSTRIP'] = self.__hexpvar.get()
