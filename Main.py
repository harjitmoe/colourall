"""ColourAll %(__version__)s

ORIGINAL AUTHOR: Barry Warsaw <barry@python.org>

MODIFIED by THH

Introduction (THH)
==================

    I discovered this in the Python distribution (under the name 
    Pynche) and decided that there were numerous improvements I could
    make.  I gave it a self-contained palette, so it does not rely on
    external pallettes, and can do a best-of all in the colour list. 
    I improved said colour list giving it an improved interface, a 
    place in the main GUI and different sorting methods.
    
    It is portable and (given appropriate tools) compilable to EXE. 
    
    Pynche had a "constants" mode commented out.  I got it working 
    and integrated it under a user friendly name.

Original Introduction (Barry Warsaw)
====================================

    Pynche is a color editor based largely on a similar program that I
    originally wrote back in 1987 for the Sunview window system.  That
    editor was called ICE, the Interactive Color Editor.  I'd always
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
    very colormap intensive, so it doesn't work very well on 8-bit
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

    initialcolor
        a Tk color name or #rrggbb color spec to be used as the
        initially selected color.  This overrides any color saved in
        the persistent init file.  Since `#' needs to be escaped in
        many shells, it is optional in the spec (e.g. #45dd1f is the
        same as 45dd1f).


  Running as a Modal Dialog
  -------------------------

    ColourAll can be run as a modal dialog, inside another application,
    say as a general color chooser.  ColourAll supports the API
    implemented by the Tkinter standard tkColorChooser module, with a
    few changes as described below.  By importing caColorChooser from
    the ColourAll package, you can run

        caColorChooser.askcolor()

    which will popup ColourAll as a modal dialog, and return the 
    selected color.

    There are some UI differences when running as a modal
    vs. standalone.  When running as a modal, there is no "Quit" menu
    item under the "File" menu.  Instead there are "Okay" and "Cancel"
    buttons.

    When "Okay" is hit, askcolor() returns the tuple

        ((r, g, b), "name")

    where r, g, and b are red, green, and blue color values
    respectively (in the range 0 to 255).  "name" will be a color name
    from the color database if there is an exact match, otherwise it
    will be a hex color spec of the form "#rrggbb".  Note that this
    is different than tkColorChooser, which doesn't know anything
    about color names.

    askcolor() supports the following optional keyword arguments:

        color
            the color to set as the initial selected color

        master[*]
            the master window to use as the parent of the modal
            dialog.  Without this argument, pyColorChooser will create 
            its own Tkinter.Tk instance as the master.  This may not
            be what you want.

        wantspec
            When this is true, the "name" field in the return tuple
            will always be a color spec of the form "#rrggbb".  It
            will not return a color name even if there is a match;
            this is so pyColorChooser can exactly match the API of
            tkColorChooser.

        [*] these arguments must be specified the first time
        askcolor() is used and cannot be changed on subsequent calls.

Integrated Views
================

  The Colorstrip Window
  ---------------------

    The top part of the main ColourAll window contains the "variation
    strips".  Each strip contains a number of "color chips".  The
    strips always indicate the currently selected color by a highlight
    rectangle around the selected color chip, with an arrow pointing
    to the chip.  Each arrow has an associated number giving you the
    color value along the variation's axis.  Each variation strip
    shows you the colors that are reachable from the selected color by
    varying just one axis of the color solid.

    For example, when the selected color is (in Red/Green/Blue
    notation) 127/127/127, the Red Variations strip shows you every
    color in the range 0/127/127 to 255/127/127.  Similarly for the
    green and blue axes.  You can select any color by clicking on its
    chip.  This will update the highlight rectangle and the arrow, as
    well as other displays in ColourAll.

    Click on "Update while dragging" if you want ColourAll to update 
    the selected color while you drag along any variation strip (this 
    will be a bit slower).  Click on "Hexadecimal" to display the 
    arrow numbers in hex.

    There are also two shortcut buttons in this window, which
    auto-select Black (0/0/0) and White (255/255/255).


  The Proof Window
  ----------------

    In the lower left corner of the main window you see two larger
    color chips.  The Selected chip shows you a larger version of the
    color selected in the variation strips, along with its hex color
    specification.  The Nearest chip shows you the closest color in
    the database to the selected color, giving its hex color
    specification, and below that, its color name.  When the
    Selected chip color exactly matches the Nearest chip color, you
    will see the color name appear below the color specification for
    the Selected chip.
    
    Clicking on the Nearest color chip selects that color.  Color
    distance is calculated in the 3D space of the RGB color solid and
    if more than one color name is the same distance from the selected
    color, the first one found will be chosen.

    Note that there may be more than one color name for the same
    RGB value.  In that case, the first one found in the text database
    is designated the "primary" name, and this is shown under the
    Nearest chip.  The other names are "aliases" and they are visible
    in the Color List Window (see below).

    Both the color specifications and color names are selectable for
    copying and pasting into another window.


  The Type-in Window
  ------------------

    At the lower right of the main window are three entry fields.
    Here you can type numeric values for any of the three color axes.
    Legal values are between 0 and 255, and these fields do not allow
    you to enter illegal values.  You must hit Enter or Tab to select
    the new color.

    Click on "Update while typing" if you want ColourAll to select 
    the color on every keystroke (well, every one that produces a 
    legal value!)  Click on "Hexadecimal" to display and enter color 
    values in hex.

  The Color List Window
  ---------------------

    The "Color List" window shows every named color in the color name
    database, it is now in ColourAll's right panel.  In the upper
    part of the window you see a scrolling list of all the color names
    in the database, in alphabetical order.  Click on any color to
    select it.  In the bottom part of the window is displayed any
    aliases for the selected color (those color names that have the
    same RGB value, but were found later in the text database).  For
    example, find the color "Aqua" and you'll see that its alias is
    "Cyan".

    If the color has no aliases you'll see "<no aliases>" here.  If you
    just want to see if a color has an alias, and do not want to select a
    color when you click on it, turn off "Update on Click".

    Note that the color list is always updated when a color is selected
    from the main window.  There's no way to turn this feature off.  If
    the selected color has no matching color name you'll see
    "<no matching color>" in the Aliases window.


Other Views
===========

    There are two (originally three) secondary windows which are not 
    displayed by default.  You can bring these up via the "View" menu 
    on the main ColourAll window.


  The Text Window
  ---------------

    The "Text Window" allows you to see what effects various colors
    have on the standard Tk text widget elements.  In the upper part
    of the window is a plain Tk text widget and here you can edit the
    text, select a region of text, etc.  Below this is a button "Track
    color changes".  When this is turned on, any colors selected in
    the other windows will change the text widget element specified in
    the radio buttons below.  When this is turned off, text widget
    elements are not affected by color selection.

    You can choose which element gets changed by color selection by
    clicking on one of the radio buttons in the bottom part of this
    window.  Text foreground and background affect the text in the
    upper part of the window.  Selection foreground and background
    affect the colors of the primary selection which is what you see
    when you click the middle button (depending on window system) and
    drag it through some text.

    The Insertion is the insertion cursor in the text window, where
    new text will be inserted as you type.  The insertion cursor only
    has a background.


  The Details Window
  ------------------

    The "Details" window gives you more control over color selection
    than just clicking on a color chip in the main window.  The row of
    buttons along the top apply the specified increment and decrement
    amounts to the selected color.  These delta amounts are applied to
    the variation strips specified by the check boxes labeled "Move
    Sliders".  Thus if just Red and Green are selected, hitting -10
    will subtract 10 from the color value along the red and green
    variation only.  Note the message under the checkboxes; this
    indicates the primary color level being changed when more than one
    slider is tied together.  For example, if Red and Green are
    selected, you will be changing the Yellow level of the selected
    color.

    The "At Boundary" behavior determines what happens when any color
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


Color Name Databases
====================

    The original Pynche used color name database files to 
    calculate the nearest color to the selected color, and to display 
    in the Color List view.  Several files were distributed with 
    Pynche, files contributing to the bultin database are described 
    below. You can still use such database files!

    html40colors.txt -- the HTML 4.0 guaranteed colour names.  Was 
    guaranteed to contribute to the list.

    webcolors.txt -- The 140 colour names that Tim Peters and his
    sister say NS and MSIE both understand (with some controversy 
    over AliceBlue). Was included.

    rgb.txt -- the colour names from X11 (which is licensed as
    below). Maroon was renamed to RichMaroon and Purple to Veronica 
    due to clashes with W3C. And the license I mentioned earlier is:

     X Window System License - X11R6.4

     Copyright (c) 1998 The Open Group

     Permission is hereby granted, free of charge, to any person obtaining
     a copy of this software and associated documentation files (the
     "Software"), to deal in the Software without restriction, including
     without limitation the rights to use, copy, modify, merge, publish,
     distribute, sublicense, and/or sell copies of the Software, and to
     permit persons to whom the Software is furnished to do so, subject to
     the following conditions:

     The above copyright notice and this permission notice shall be
     included in all copies or substantial portions of the Software.

     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
     IN NO EVENT SHALL THE OPEN GROUP BE LIABLE FOR ANY CLAIM, DAMAGES OR
     OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
     ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
     OTHER DEALINGS IN THE SOFTWARE.

     Except as contained in this notice, the name of The Open Group shall
     not be used in advertising or otherwise to promote the sale, use or
     other dealings in this Software without prior written authorization
     from The Open Group.

     X Window System is a trademark of The Open Group

    namedcolors.txt -- an alternative set of Netscape colors?
    Contributed any colours not otherwise present.
    Retrieved from http://www.lightlink.com/xine/bells/namedcolors.html
    
    Extra databases contributing to the builtin are detailed below:
    
    (Crayola Databases) -- colours used by Crayola to describe their 
    crayons.  From Wikipedia, so under the Creative Commons Attribution
    ShareAlike 3.0 Unported, and maybe additional terms at 
    http://en.wikipedia.org/wiki/Terms_of_use . Content retrieved from 
    http://en.wikipedia.org/wiki/List_of_Crayola_crayon_colors, author
    list can be obtained at:
http://en.wikipedia.org/wiki/List_of_Crayola_crayon_colors?action=history
    
    Retsof Online Version of ISCC-NBS Dictionary of Colour Names --
    Copyright (c) 2004-2005 Voluntocracy. Permission is granted to copy 
    and distribute modified or unmodified versions of this color 
    dictionary provided the copyright notice and this permission notice 
    are preserved on all copies and the entire such work is distributed 
    under the terms of a permission notice identical to this one.
    The notice "Website page design and content Copyright (c)2000-2006 
    John C. Foster and Texas Precancel Club - All Rights Reserved. Awards 
    images are the property of the respective award program owners and 
    used with permission." was also present but would appear not to apply
    specifically to said table.

"""





__version__ = '1.0'

__doc__=__doc__%globals()
import sys
import os
import getopt
import ColorDB

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

def initial_color(s, colordb):
    # function called on every color
    def scan_color(s, colordb=colordb):
        try:
            r, g, b = colordb.find_byname(s)
        except ColorDB.BadColor:
            try:
                r, g, b = ColorDB.rrggbb_to_triplet(s)
            except (ColorDB.BadColor,ValueError):
                return None, None, None
        return r, g, b
    #
    # First try the passed in color
    r, g, b = scan_color(s)
    if r is None:
        # try the same color with '#' prepended, since some shells require
        # this to be escaped, which is a pain
        r, g, b = scan_color('#' + s)
    if r is None:
        print 'Bad initial color, using gray50:', s
        r, g, b = scan_color('gray50')
    if r is None:
        usage(1, 'Cannot find an initial color to use')
        # does not return
    return r, g, b


#from ColourAllWidget import get_colordb

def build(master=None, initialcolor="#808080", initfile=None, ignore=None,
          dbfile=None):
    global app,s
    if not initialcolor:
        initialcolor="#808080"
    
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

    s.update_views(*initial_color(initialcolor,s.colordb()))
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
        initialcolor = None
    elif len(args) == 1:
        initialcolor = args[0]
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

    app, sb = build(initialcolor=initialcolor,
                    initfile=initfile,
                    ignore=ignore,
                    dbfile=dbfile)
    run(app, sb)

if __name__=="__main__":
    main()

