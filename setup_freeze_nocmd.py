#FIXME - assumes python 2.5 and that libpython25 is static

from Freeze import makefreeze, __path__ as freezepath
freezepath=freezepath[0]
import modulefinder
import os,shutil,sys

basename="colourall"

if not os.path.exists("build"):
	os.mkdir("build")
if not os.path.exists("dist"):
	os.mkdir("dist")

import distutils.msvccompiler
pydir=os.path.dirname(os.path.abspath(sys.executable))

if "MSC" in sys.version:
	dll=int(distutils.msvccompiler.get_build_version()*10)
	if dll<=60:
		dll="r"
	dll="msvcr"+str(dll)+".dll"
	if os.path.exists(os.path.join(pydir,dll)):
		shutil.copy(os.path.join(pydir,dll),os.path.join("dist",dll))
	elif os.path.exists(os.path.join("C:\\Windows\\System32",dll)):
		shutil.copy(os.path.join("C:\\Windows\\System32",dll),os.path.join("dist",dll))
	elif os.path.exists(os.path.join("C:\\Windows\\System",dll)):
		shutil.copy(os.path.join("C:\\Windows\\System",dll),os.path.join("dist",dll))
	elif os.path.exists(os.path.join("C:\\Windows",dll)):
		shutil.copy(os.path.join("C:\\Windows",dll),os.path.join("dist",dll))
	else:
		print "WARNING: MS Visual C Runtime not found"
if os.path.exists(os.path.join(pydir,"w9xpopen.exe")):
	shutil.copy(os.path.join(pydir,"w9xpopen.exe"),os.path.join("dist","w9xpopen.exe"))

def MakeTkBootstrapper():
	import FixTk
	data="""
import sys,os,shutil,atexit
progdir=os.path.dirname(os.path.abspath(sys.executable))
rootfol=os.path.join(progdir,"tcl")
if os.path.exists(rootfol):
	shutil.rmtree(rootfol) #XXX The best way?
os.mkdir(rootfol)
os.environ['TCL_LIBRARY']=os.path.join(rootfol,"tcl")
os.mkdir(os.environ['TCL_LIBRARY'])
os.environ['TK_LIBRARY']=os.path.join(rootfol,"tk")
os.mkdir(os.environ['TK_LIBRARY'])

os.mkdir(os.path.join(os.environ['TCL_LIBRARY'],"encoding"))
open(os.path.join(os.environ['TCL_LIBRARY'],"encoding/ascii.enc"),"wb").write(%r)

os.mkdir(os.path.join(os.environ['TK_LIBRARY'],"msgs"))
open(os.path.join(os.environ['TK_LIBRARY'],"msgs/en.msg"),"wb").write(%r)

def hook(shutil=shutil,dir=rootfol):
		shutil.rmtree(dir)
atexit.register(hook)

"""%( open(os.path.join(os.environ['TCL_LIBRARY'],"encoding/ascii.enc"),"rb").read(), open(os.path.join(os.environ['TK_LIBRARY'],"msgs/en.msg"),"rb").read() )
	for i in os.listdir(os.environ['TCL_LIBRARY']):
		if os.path.isdir(os.path.join(os.environ['TCL_LIBRARY'],i)):
			continue
		else:
			data+="open(os.path.join(os.environ['TCL_LIBRARY'],%r),'wb').write(%r)\n"%(i,open(os.path.join(os.environ['TCL_LIBRARY'],i),"rb").read())
	for i in os.listdir(os.environ['TK_LIBRARY']):
		if os.path.isdir(os.path.join(os.environ['TK_LIBRARY'],i)):
			continue
		else:
			data+="open(os.path.join(os.environ['TK_LIBRARY'],%r),'wb').write(%r)\n"%(i,open(os.path.join(os.environ['TK_LIBRARY'],i),"rb").read())
	return data
			

finder=modulefinder.ModuleFinder(debug=1)
scrap=os.urandom(4).encode("hex")+"."+os.urandom(1).encode("hex")
open(scrap,"wb").write("import sys,os,tempfile,shutil,atexit,encodings,encodings.ascii")
finder.run_script(scrap)
os.unlink(scrap)
finder.run_script(basename+".pyw")
print "Skipped",finder.badmodules.keys()

class new_site:
	def __init__(self):
		self.__name__="site"
		self.__file__=os.path.join(freezepath,"newsite.py")
		self.__code__=compile(open(self.__file__,"rU").read(),self.__file__,"exec")
		self.__path__=None

finder.modules["site"]=new_site()

for modname,module in finder.modules.items():
	if not module.__code__: #Not python or bytecode
		if module.__file__: #Not builtin
			#Must be extension module then
			mf=module.__file__
			if os.name=="nt":
				mf=module.__name__+".dll"
			else:
				mf=module.__name__+".so"
			fmf=os.path.abspath(os.path.join("dist",mf))
			shutil.copy2(module.__file__,fmf)
			code="import sys,imp,os\nprogdir=os.path.dirname(os.path.abspath(sys.executable))\nsys.modules[__name__]=imp.load_dynamic(__name__,os.path.join(progdir,%r))"%mf
			if module.__name__=="_tkinter":
				code=MakeTkBootstrapper()+"\n"+code
				for i in os.listdir(os.path.join(pydir,"DLLs")):
					if i.startswith("tk") and i.endswith(".dll"):
						shutil.copy(os.path.join(pydir,"DLLs",i),os.path.join("dist",i))
					if i.startswith("tcl") and i.endswith(".dll"):
						shutil.copy(os.path.join(pydir,"DLLs",i),os.path.join("dist",i))
			module.__code__=compile(code,mf+"(launcher)","exec")

os.chdir("build")
makefreeze.makefreeze(basename,finder.modules)
n=["gcc","-mwindows","-IC:\\Python25\\include","-LC:\\Python25\\libs"]+filter(lambda i:i.startswith(basename) and i.endswith(".c"),os.listdir("."))+[os.path.join(freezepath,"frozenmain.c"),"-lpython25","-o../dist/%s.exe"%basename]
os.spawnv(os.P_WAIT,"C:\\strawberry\\c\\bin\gcc.exe",n)
os.chdir(os.pardir)
