"""ColourAll %(__version__)s

ORIGINAL AUTHOR: Barry Warsaw <barry@python.org>

MODIFIED by THH

Introduction (THH)
==================

    I discovered this in the Python distribution (under the name 
    Pynche) and decided that there were numerous improvements I could
    make.  I gave it a self-contained palette, so it does not rely on
    external palettes, and can do a best-of all in the colour list
    (but it does look for certain external palettes to incorporate). 
    I improved said colour list giving it an improved interface, a 
    place in the main GUI and different sorting methods.
    
    It is portable and (given appropriate tools) compilable to EXE. 
    
    Pynche had a "constants" mode commented out.  I got it working 
    and integrated it under a user friendly name.

Original Introduction (Barry Warsaw)
====================================

    Pynche is a colour editor based largely on a similar program that I
    originally wrote back in 1987 for the Sunview window system.  That
    editor was called ICE, the Interactive Colour Editor.  I'd always
    wanted to port this program to X but didn't feel like hacking X
    and C code to do it.  Fast forward many years, to where Python +
    Tkinter provides such a nice programming environment, with enough
    power, that I finally buckled down and re-implemented it.  I
    changed the name because these days, too many other systems have
    the acronym `ICE'.

    Pynche should work with any variant of Python after 1.5.2
    (e.g. 2.0.1 and 2.1.1), using Tk 8.0.x.  It's been tested on
    Solaris 2.6, Windows NT 4, and various Linux distros.  You'll want
    to be sure to have at least Tk 8.0.3 for Windows.  Also, Pynche is
    very colourmap intensive, so it doesn't work very well on 8-bit
    graphics cards; 24bit+ graphics cards are so cheap these days,
    I'll probably never "fix" that.

Running
=======

  Running Standalone
  ------------------

    On Unix, start it by running the `colourall' script.  On Windows, 
    run colourall.pyw to inhibit the console window.  When run from 
    the command line, the following options are recognized:

    --help
    -h
        Print the help message.

    initialcolour
        a Tk colour name or #rrggbb colour spec to be used as the
        initially selected colour.  This overrides any colour saved in
        the persistent init file.  Since `#' needs to be escaped in
        many shells, it is optional in the spec (e.g. #45dd1f is the
        same as 45dd1f).


  Running as a Modal Dialog
  -------------------------

    ColourAll can be run as a modal dialog, inside another application,
    say as a general colour chooser.  ColourAll supports the API
    implemented by the Tkinter standard tkColourChooser module, with a
    few changes as described below.  By importing caColourChooser from
    the ColourAll package, you can run

        caColourChooser.askcolour()

    which will popup ColourAll as a modal dialog, and return the 
    selected colour.

    There are some UI differences when running as a modal
    vs. standalone.  When running as a modal, there is no "Quit" menu
    item under the "File" menu.  Instead there are "Okay" and "Cancel"
    buttons.

    When "Okay" is hit, askcolour() returns the tuple

        ((r, g, b), "name")

    where r, g, and b are red, green, and blue colour values
    respectively (in the range 0 to 255).  "name" will be a colour name
    from the colour database if there is an exact match, otherwise it
    will be a hex colour spec of the form "#rrggbb".  Note that this
    is different than tkColourChooser, which doesn't know anything
    about colour names.

    askcolour() supports the following optional keyword arguments:

        colour
            the colour to set as the initial selected colour

        master[*]
            the master window to use as the parent of the modal
            dialog.  Without this argument, pyColourChooser will create 
            its own Tkinter.Tk instance as the master.  This may not
            be what you want.

        wantspec
            When this is true, the "name" field in the return tuple
            will always be a colour spec of the form "#rrggbb".  It
            will not return a colour name even if there is a match;
            this is so pyColourChooser can exactly match the API of
            tkColourChooser.

        [*] these arguments must be specified the first time
        askcolour() is used and cannot be changed on subsequent calls.

Integrated Views
================

  The Colourstrip Window
  ---------------------

    The top part of the main ColourAll window contains the "variation
    strips".  Each strip contains a number of "colour chips".  The
    strips always indicate the currently selected colour by a highlight
    rectangle around the selected colour chip, with an arrow pointing
    to the chip.  Each arrow has an associated number giving you the
    colour value along the variation's axis.  Each variation strip
    shows you the colours that are reachable from the selected colour by
    varying just one axis of the colour solid.

    For example, when the selected colour is (in Red/Green/Blue
    notation) 127/127/127, the Red Variations strip shows you every
    colour in the range 0/127/127 to 255/127/127.  Similarly for the
    green and blue axes.  You can select any colour by clicking on its
    chip.  This will update the highlight rectangle and the arrow, as
    well as other displays in ColourAll.

    Click on "Update while dragging" if you want ColourAll to update 
    the selected colour while you drag along any variation strip (this 
    will be a bit slower).  Click on "Hexadecimal" to display the 
    arrow numbers in hex.

    There are also two shortcut buttons in this window, which
    auto-select Black (0/0/0) and White (255/255/255).


  The Proof Window
  ----------------

    In the lower left corner of the main window you see two larger
    colour chips.  The Selected chip shows you a larger version of the
    colour selected in the variation strips, along with its hex colour
    specification.  The Nearest chip shows you the closest colour in
    the database to the selected colour, giving its hex colour
    specification, and below that, its colour name.  When the
    Selected chip colour exactly matches the Nearest chip colour, you
    will see the colour name appear below the colour specification for
    the Selected chip.
    
    Clicking on the Nearest colour chip selects that colour.  Colour
    distance is calculated in the 3D space of the RGB colour solid and
    if more than one colour name is the same distance from the selected
    colour, the first one found will be chosen.

    Note that there may be more than one colour name for the same
    RGB value.  In that case, the first one found in the text database
    is designated the "primary" name, and this is shown under the
    Nearest chip.  The other names are "aliases" and they are visible
    in the Colour List Window (see below).

    Both the colour specifications and colour names are selectable for
    copying and pasting into another window.


  The Type-in Window
  ------------------

    At the lower right of the main window are three entry fields.
    Here you can type numeric values for any of the three colour axes.
    Legal values are between 0 and 255, and these fields do not allow
    you to enter illegal values.  You must hit Enter or Tab to select
    the new colour.

    Click on "Update while typing" if you want ColourAll to select 
    the colour on every keystroke (well, every one that produces a 
    legal value!)  Click on "Hexadecimal" to display and enter colour 
    values in hex.

  The Colour List Window
  ---------------------

    The "Colour List" window shows every named colour in the colour name
    database, it is now in ColourAll's right panel.  In the upper
    part of the window you see a scrolling list of all the colour names
    in the database, in alphabetical order.  Click on any colour to
    select it.  In the bottom part of the window is displayed any
    aliases for the selected colour (those colour names that have the
    same RGB value, but were found later in the text database).  For
    example, find the colour "Aqua" and you'll see that its alias is
    "Cyan".

    If the colour has no aliases you'll see "<no aliases>" here.  If you
    just want to see if a colour has an alias, and do not want to select a
    colour when you click on it, turn off "Update on Click".

    Note that the colour list is always updated when a colour is selected
    from the main window.  There's no way to turn this feature off.  If
    the selected colour has no matching colour name you'll see
    "<no matching colour>" in the Aliases window.


Other Views
===========

    There are two (originally three) secondary windows which are not 
    displayed by default.  You can bring these up via the "View" menu 
    on the main ColourAll window.


  The Text Window
  ---------------

    The "Text Window" allows you to see what effects various colours
    have on the standard Tk text widget elements.  In the upper part
    of the window is a plain Tk text widget and here you can edit the
    text, select a region of text, etc.  Below this is a button "Track
    colour changes".  When this is turned on, any colours selected in
    the other windows will change the text widget element specified in
    the radio buttons below.  When this is turned off, text widget
    elements are not affected by colour selection.

    You can choose which element gets changed by colour selection by
    clicking on one of the radio buttons in the bottom part of this
    window.  Text foreground and background affect the text in the
    upper part of the window.  Selection foreground and background
    affect the colours of the primary selection which is what you see
    when you click the middle button (depending on window system) and
    drag it through some text.

    The Insertion is the insertion cursor in the text window, where
    new text will be inserted as you type.  The insertion cursor only
    has a background.


  The Details Window
  ------------------

    The "Details" window gives you more control over colour selection
    than just clicking on a colour chip in the main window.  The row of
    buttons along the top apply the specified increment and decrement
    amounts to the selected colour.  These delta amounts are applied to
    the variation strips specified by the check boxes labeled "Move
    Sliders".  Thus if just Red and Green are selected, hitting -10
    will subtract 10 from the colour value along the red and green
    variation only.  Note the message under the checkboxes; this
    indicates the primary colour level being changed when more than one
    slider is tied together.  For example, if Red and Green are
    selected, you will be changing the Yellow level of the selected
    colour.

    The "At Boundary" behavior determines what happens when any colour
    variation hits either the lower or upper boundaries (0 or 255) as
    a result of clicking on the top row buttons:

    Stop
        When the increment or decrement would send any of the tied
        variations out of bounds, the entire delta is discarded.

    Wrap Around
        When the increment or decrement would send any of the tied
        variations out of bounds, the out of bounds value is wrapped
        around to the other side.  Thus if red were at 238 and +25
        were clicked, red would have the value 7.

    Preserve Distance
        When the increment or decrement would send any of the tied
        variations out of bounds, all tied variations are wrapped as
        one, so as to preserve the distance between them.  Thus if
        green and blue were tied, and green was at 238 while blue was
        at 223, and +25 were clicked, green would be at 15 and blue
        would be at 0.

    Squash
        When the increment or decrement would send any of the tied
        variations out of bounds, the out of bounds variation is set
        to the ceiling of 255 or floor of 0, as appropriate.  In this
        way, all tied variations are squashed to one edge or the
        other.

    The top row buttons have the following keyboard accelerators:

    -25 == Shift Left Arrow
    -10 == Control Left Arrow
     -1 == Left Arrow
     +1 == Right Arrow
    +10 == Control Right Arrow
    +25 == Shift Right Arrow


Keyboard Accelerators
=====================

    Alt-w in any secondary window dismisses the window.  In the main
    window it exits ColourAll (except when running as a modal).

    Alt-q in any window exits ColourAll (except when running as a modal).


Colour Name Databases
====================

    Colour name database files are used to 
    calculate the nearest colour to the selected colour, and to display 
    in the Colour List view.

    While an initial database is used as an attempted merger of those
    supplied, you may load them individually.

"""





__version__ = '1.3'

__doc__=__doc__%globals()
import sys
import os
import getopt
import ColourDB

import ColourAllWidget
ColourAllWidget.docs=__doc__

from ColourAllWidget import ColourAllWidget
from Switchboard import Switchboard
from StripViewer import StripViewer
from ChipViewer import ChipViewer
from ListViewer import ListViewer
from TypeinViewer import TypeinViewer
from Tkinter import Tk,Text,Scrollbar
from Tkconstants import *
import tkMessageBox


PROGRAM = sys.argv[0]
AUTHNAME = ''
AUTHEMAIL = ''



# Do this because ColourAllWidget.py wants to get at the interpolated docstring
# too, for its Help menu.
def docstring():
    return __doc__ % globals()


def usage(code, msg=''):
    global __doc__,app,s
    try:
        app._ColourAllWidget__tkroot.destroy()
    except AttributeError:
        raise
    except NameError:
        pass
    app,s=build()
    app._ColourAllWidget__keepalive()
    app._ColourAllWidget__popup_usage()
    if code and not msg:
        msg="Error in calling convention. \nPlease see help for usage info."
    if msg:
        tkMessageBox.showerror("ColourAll "+__version__,msg,master=app._ColourAllWidget__tkroot)
    app._ColourAllWidget__tkroot.mainloop()
    sys.exit(code)


def version():
    app,s=build()
    app._ColourAllWidget__keepalive()
    app._ColourAllWidget__popup_about()
    app._ColourAllWidget__tkroot.mainloop()
    sys.exit(0)

def initial_colour(s, colourdb):
    # function called on every colour
    def scan_colour(s, colourdb=colourdb):
        try:
            r, g, b = colourdb.find_byname(s)
        except ColourDB.BadColour:
            try:
                r, g, b = ColourDB.rrggbb_to_triplet(s)
            except (ColourDB.BadColour,ValueError):
                return None, None, None
        return r, g, b
    #
    # First try the passed in colour
    r, g, b = scan_colour(s)
    if r is None:
        # try the same colour with '#' prepended, since some shells require
        # this to be escaped, which is a pain
        r, g, b = scan_colour('#' + s)
    if r is None:
        print 'Bad initial colour, using gray50:', s
        r, g, b = scan_colour('gray50')
    if r is None:
        usage(1, 'Cannot find an initial colour to use')
        # does not return
    return r, g, b


#from ColourAllWidget import get_colourdb

def build(master=None, initialcolour="#808080", initfile=None, ignore=None,
          dbfile=None):
    global app,s
    if not initialcolour:
        initialcolour="#808080"
    
    # create all output widgets
    s = Switchboard(0)

    # create the application window decorations
    app = ColourAllWidget(__version__, s, master=master)
    w = app.window()

    # these built-in viewers live inside the main ColourAll window
    s.add_view(StripViewer(s, w))
    s.add_view(ChipViewer(s, w))
    s.add_view(TypeinViewer(s, w))
    s.add_view(ListViewer(s, w))

    s.update_views(*initial_colour(initialcolour,s.colourdb()))
    return app, s


def run(app, s):
    try:
        app.start()
    except KeyboardInterrupt:
        pass


def main():
    global app,sb
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hv',
            ['help', 'version'])
    except getopt.error, msg:
        usage(1, msg)

    if len(args) == 0:
        initialcolour = None
    elif len(args) == 1:
        initialcolour = args[0]
    else:
        usage(1)

    ignore = 0
    dbfile = None
    initfile = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-v', '--version'):
            version()

    app, sb = build(initialcolour=initialcolour,
                    initfile=initfile,
                    ignore=ignore,
                    dbfile=dbfile)
    run(app, sb)

if __name__=="__main__":
    main()

