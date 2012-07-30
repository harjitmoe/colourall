"""Colour chooser implementing (almost) the tkColorChoser interface

This should use "color" (USA) where it affects the API, in docstrings
and everything else "colour" (UK) is preferred.
"""

import os
import Main
import ColorDB



class Chooser:
    """Ask for a colour"""
    def __init__(self,
                 master = None,
                 databasefile = None,
                 initfile = None,
                 ignore = None,
                 wantspec = None):
        self.__master = master
        self.__databasefile = databasefile
        self.__initfile = initfile or os.path.expanduser('~/.colral')
        self.__ignore = ignore
        self.__pw = None
        self.__wantspec = wantspec

    def show(self, colour, options):
        # scan for options that can override the ctor options
        self.__wantspec = options.get('wantspec', self.__wantspec)
        dbfile = options.get('databasefile', self.__databasefile)
        # load the database file
        colourdb = None
        if dbfile <> self.__databasefile:
            colourdb = ColorDB.get_colourdb(dbfile)
        if not self.__master:
            from Tkinter import Tk
            self.__master = Tk()
        if not self.__pw:
            self.__pw, self.__sb = \
                       Main.build(master = self.__master,
                                  initfile = self.__initfile,
                                  ignore = self.__ignore)
        else:
            self.__pw.deiconify()
        # convert colour
        if colourdb:
            self.__sb.set_colourdb(colourdb)
        else:
            colourdb = self.__sb.colordb()
        if colour:
            r, g, b = Main.initial_color(colour, colourdb)
            self.__sb.update_views(r, g, b)
        # reset the canceled flag and run it
        self.__sb.canceled(0)
        Main.run(self.__pw, self.__sb)
        rgbtuple = self.__sb.current_rgb()
        self.__pw.withdraw()
        # check to see if the cancel button was pushed
        if self.__sb.canceled_p():
            return None, None
        # Try to return the colour name from the database if there is an exact
        # match, otherwise use the "#rrggbb" spec.  BAW: Forget about colour
        # aliases for now, maybe later we should return these too.
        name = None
        if not self.__wantspec:
            try:
                name = colourdb.find_byrgb(rgbtuple)[0]
            except ColorDB.BadColour:
                pass
        if name is None:
            name = ColorDB.triplet_to_rrggbb(rgbtuple)
        return rgbtuple, name

    def save(self):
        if self.__sb:
            self.__sb.save_views()


# convenience stuff
_chooser = None

def askcolor(colour = None, **options):
    """Ask for a colour"""
    global _chooser
    if not _chooser:
        _chooser = apply(Chooser, (), options)
    return _chooser.show(colour, options)

def save():
    global _chooser
    if _chooser:
        _chooser.save()


# test stuff
if __name__ == '__main__':
    from Tkinter import *

    class Tester:
        def __init__(self):
            self.__root = tk = Tk()
            b = Button(tk, text='Choose Colour...', command=self.__choose)
            b.pack()
            self.__l = Label(tk)
            self.__l.pack()
            q = Button(tk, text='Quit', command=self.__quit)
            q.pack()

        def __choose(self, event=None):
            rgb, name = askcolor(master=self.__root)
            if rgb is None:
                text = 'You hit CANCEL!'
            else:
                r, g, b = rgb
                text = 'You picked %s (%3d/%3d/%3d)' % (name, r, g, b)
            self.__l.configure(text=text)

        def __quit(self, event=None):
            self.__root.quit()

        def run(self):
            self.__root.mainloop()
    t = Tester()
    t.run()
    # simpler
##    print 'colour:', askcolor()
##    print 'colour:', askcolor()
