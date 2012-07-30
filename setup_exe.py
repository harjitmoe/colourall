#!C:\Python25\python.exe
import sys,os,Tkinter,tkMessageBox,tkFileDialog
_app="EXE"

root=Tkinter.Tk()
root.title(_app)

import py2exe
from distutils.core import setup

pys=[]
pyws=[]
    
def setitup():
    i = tkFileDialog.askopenfilename(
        filetypes=[("Python", "*.py*"),("All Files","*.*")], 
        title="Please select a python program to compile to exe:", 
        parent=root
    )

    if i.endswith('.pyw'):
        pyws.append(i)
    else:
        pys.append(i)

    if len(sys.argv) == 1:
        sys.argv.append("py2exe")
        sys.argv.append("-q")

    single=tkMessageBox.askyesno(_app,"Single file?\nUSE NO WITH TKinter PROGRAMS: ")

    if single:
        options={
            "py2exe":{
                "compressed": 1,
                "optimize": 0,
                "ascii": 1,
                "bundle_files": 1
            }
        }
    else:
        options={"py2exe": {}}
    
    setup(
        options = options,
        zipfile = None,
        windows = pyws,
        console = pys
    )

button=Tkinter.Button(root,command=setitup,text="Start")
button.pack()
abort=Tkinter.Button(root,command=sys.exit,text="Exit")
abort.pack()
root.mainloop()
