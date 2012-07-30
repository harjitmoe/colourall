import sys,__builtin__
if hasattr(sys,"setdefaultencoding"):
	sys.setdefaultencoding("ascii")
try:
	import sitecustomize
except ImportError:
	pass

sys.path=[]

#The above by THH
#The below from Python's site.py, tweaked for simplicity by THH

__builtin__.copyright = sys.copyright
__builtin__.credits = """\
Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands
for supporting Python development.  See www.python.org for more information."""
__builtin__.license = "License availible at http://www.python.org/%.3s/license.html" #XXX