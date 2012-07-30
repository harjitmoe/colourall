"""Main ColourAll (Pythonically Natural Colour and Hue Editor) widget.

This window provides the basic decorations, primarily including the menubar.
It is used to bring up other windows.
"""

import sys
import os
from Tkinter import *
import tkMessageBox
import tkFileDialog
import ColourDB,StringIO

# Milliseconds between interrupt checks
KEEPALIVE_TIMER = 500

def get_colourdb(filetype=None):
    import ColourStores
    return ColourStores.unicolour

class ColourAllWidget:
    def __init__(self, version, switchboard, master=None, extrapath=[]):
        self.__sb = switchboard
        self.__version = version
        self.__textwin = None
        self.__listwin = None
        self.__detailswin = None
        self.__helpwin = None
        self.__dialogstate = {}
        modal = self.__modal = not not master
        # If a master was given, we are running as a modal dialog servant to
        # some other application.  We rearrange our UI in this case (there's
        # no File menu and we get `Okay' and `Cancel' buttons), and we do a
        # grab_set() to make ourselves modal
        if modal:
            self.__tkroot = tkroot = Toplevel(master, class_='ColourAll')
            tkroot.grab_set()
            tkroot.withdraw()
        else:
            # Is there already a default root for Tk, say because we're
            # running under Guido's IDE? :-) Two conditions say no, either the
            # import fails or _default_root is None.
            tkroot = None
            try:
                from Tkinter import _default_root
                tkroot = self.__tkroot = _default_root
            except ImportError:
                pass
            if not tkroot:
                tkroot = self.__tkroot = Tk(className='ColourAll')
            # but this isn't our top level widget, so make it invisible
            tkroot.withdraw()
        # create the menubar
        menubar = self.__menubar = Menu(tkroot)
        #
        # File menu
        #
        filemenu = self.__filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Load alternate palette...',
                             command=self.__load,
                             underline=0)
        filemenu.add_command(label='Reset palette...',
                             command=self.__intern_pal,
                             underline=0)
        if not modal:
            filemenu.add_command(label='Quit',
                                 command=self.__quit,
                                 accelerator='Alt-Q',
                                 underline=0)
        #
        # View menu
        #
        views = make_view_popups(self.__sb, self.__tkroot, extrapath)
        viewmenu = Menu(menubar, tearoff=0)
        for v in views:
            viewmenu.add_command(label=v.menutext(),
                                 command=v.popup,
                                 underline=v.underline())
        #
        # Help menu
        #
        helpmenu = Menu(menubar, name='help', tearoff=0)
        helpmenu.add_command(label='About ColourAll...',
                             command=self.__popup_about,
                             underline=0)
        helpmenu.add_command(label='Help...',
                             command=self.__popup_usage,
                             underline=0)
        #
        # Tie them all together
        #
        menubar.add_cascade(label='File',
                            menu=filemenu,
                            underline=0)
        menubar.add_cascade(label='View',
                            menu=viewmenu,
                            underline=0)
        menubar.add_cascade(label='Help',
                            menu=helpmenu,
                            underline=0)

        # now create the top level window
        root = self.__root = Toplevel(tkroot, class_='ColourAll', menu=menubar)
        root.protocol('WM_DELETE_WINDOW',
                      modal and self.__bell or self.__quit)
        root.title('ColourAll %s' % version)
        root.iconname('ColourAll')
        # Only bind accelerators for the File->Quit menu item if running as a
        # standalone app
        if not modal:
            root.bind('<Alt-q>', self.__quit)
            root.bind('<Alt-Q>', self.__quit)
        else:
            # We're a modal dialog so we have a new row of buttons
            bframe = Frame(root, borderwidth=1, relief=RAISED)
            bframe.grid(row=4, column=0, columnspan=2,
                        sticky='EW',
                        ipady=5)
            okay = Button(bframe,
                          text='Okay',
                          command=self.__okay)
            okay.pack(side=LEFT, expand=1)
            cancel = Button(bframe,
                            text='Cancel',
                            command=self.__cancel)
            cancel.pack(side=LEFT, expand=1)
        self.__intern_pal()

    def __intern_pal(self, event=None):
        self.__sb.set_colourdb(get_colourdb())

    def __quit(self, event=None):
        self.__tkroot.quit()

    def __bell(self, event=None):
        self.__tkroot.bell()

    def __okay(self, event=None):
        self.__sb.withdraw_views()
        self.__tkroot.grab_release()
        self.__quit()

    def __cancel(self, event=None):
        self.__sb.canceled()
        self.__okay()

    def __keepalive(self):
        # Exercise the Python interpreter regularly so keyboard interrupts get
        # through.
        self.__tkroot.tk.createtimerhandler(KEEPALIVE_TIMER, self.__keepalive)

    def start(self):
        if not self.__modal:
            self.__keepalive()
        self.__tkroot.mainloop()

    def window(self):
        return self.__root

    def __popup_about(self, event=None):
        from Main import __version__
        tkMessageBox.showinfo('About ColourAll ' + __version__,
                              '''ColourAll (based on Pynche 1.4.1) %s''' % __version__)

    def __popup_usage(self, event=None):
        if not self.__helpwin:
            self.__helpwin = Helpwin(self.__root, self.__quit)
        self.__helpwin.deiconify()

    def __load(self, event=None):
        while 1:
            idir, ifile = os.path.split(self.__sb.colourdb().filename())
            file = tkFileDialog.askopenfilename(
                filetypes=[('Text files', '*.txt'),
                           ('All files', '*'),
                           ],
                initialdir=idir,
                initialfile=ifile)
            if not file:
                # cancel button
                return
            try:
                colourdb = ColourDB.get_colourdb(file)
            except IOError:
                tkMessageBox.showerror('Read error', '''\
Could not open file for reading:
%s''' % file)
                continue
            if colourdb is None:
                tkMessageBox.showerror('Unrecognized colour file type', '''\
Unrecognized colour file type in file:
%s''' % file)
                continue
            break
        self.__sb.set_colourdb(colourdb)

    def withdraw(self):
        self.__root.withdraw()

    def deiconify(self):
        self.__root.deiconify()


class Helpwin:
    def __init__(self, master, quitfunc):
        self.__root = root = Toplevel(master, class_='ColourAll')
        root.protocol('WM_DELETE_WINDOW', self.__withdraw)
        root.title('ColourAll Help Window')
        root.iconname('ColourAll Help Window')
        root.bind('<Alt-q>', quitfunc)
        root.bind('<Alt-Q>', quitfunc)
        root.bind('<Alt-w>', self.__withdraw)
        root.bind('<Alt-W>', self.__withdraw)

        contents=docs

        import tkFont
        self.__text = text = Text(root, relief=SUNKEN,
                                  width=75, height=24, font=tkFont.Font(root,family="Courier",size=10))
        self.__text.focus_set()
        text.insert(0.0, contents)
        scrollbar = Scrollbar(root)
        scrollbar.pack(fill=Y, side=RIGHT)
        text.pack(fill=BOTH, expand=YES)
        text.configure(yscrollcommand=(scrollbar, 'set'))
        scrollbar.configure(command=(text, 'yview'))

    def __withdraw(self, event=None):
        self.__root.withdraw()

    def deiconify(self):
        self.__root.deiconify()



class PopupViewer:
    def __init__(self, module, name, switchboard, root):
        self.__m = module
        self.__name = name
        self.__sb = switchboard
        self.__root = root
        self.__menutext = module.ADDTOVIEW
        # find the underline character
        underline = module.ADDTOVIEW.find('%')
        if underline == -1:
            underline = 0
        else:
            self.__menutext = module.ADDTOVIEW.replace('%', '', 1)
        self.__underline = underline
        self.__window = None

    def menutext(self):
        return self.__menutext

    def underline(self):
        return self.__underline

    def popup(self, event=None):
        if not self.__window:
            # class and module must have the same name
            class_ = getattr(self.__m, self.__name)
            self.__window = class_(self.__sb, self.__root, sa=1)
            self.__sb.add_view(self.__window)
        self.__window.deiconify()

    def __cmp__(self, other):
        return cmp(self.__menutext, other.__menutext)


def make_view_popups(switchboard, root, extrapath):
    viewers = []
    # where we are in the file system
    dirs = [os.path.dirname(__file__)] + extrapath
    for dir in dirs:
        if dir == '':
            dir = '.'
	#See also _py2exe_mf_imports() (below)
        l=['ChipViewer.py', 'DetailsViewer.py', 'ListViewer.py', 'StripViewer.py', 'TextViewer.py',  'TypeinViewer.py', 'GotoViewer']
        if sys.executable.lower().find(sys.argv[0].lower())<0: #Any better way?
            print "Non-Applet"
            l=os.listdir(dir)
        for file in l:
            if file[-9:] == 'Viewer.py':
                name = file[:-3]
                try:
                    module = __import__(name)
                except ImportError:
                    # ColourAll is running from inside a package, so get the
                    # module using the explicit path.
                    try:
                        pkg = __import__('colourall.'+name)
                        module = getattr(pkg, name)
                    except ImportError:
                        #Was removed without updating default l
                        continue
                if hasattr(module, 'ADDTOVIEW') and module.ADDTOVIEW:
                    # this is an external viewer
                    v = PopupViewer(module, name, switchboard, root)
                    viewers.append(v)
                #else:
                #    module.ADDTOVIEW=name
                #    v = PopupViewer(module, name, switchboard, root)
                #    viewers.append(v)
    # sort alphabetically
    viewers.sort()
    return viewers

def _py2exe_mf_imports(): import ChipViewer,DetailsViewer,ListViewer,StripViewer,TextViewer,TypeinViewer,GotoViewer #See also make_view_popups() (above)

