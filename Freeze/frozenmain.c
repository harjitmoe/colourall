
/* Python interpreter main program for frozen scripts */

#include "Python.h"

/* Main program */

int
Py_FrozenMain(int argc, char **argv)
{
	char *p;
	int n, sts;
	int inspect = 0;
	int unbuffered = 0;

	Py_FrozenFlag = 1; /* Suppress errors from getpath.c */

	if ((p = Py_GETENV("PYTHONINSPECT")) && *p != '\0')
		inspect = 1;
	if ((p = Py_GETENV("PYTHONUNBUFFERED")) && *p != '\0')
		unbuffered = 1;

	if (unbuffered) {
		setbuf(stdin, (char *)NULL);
		setbuf(stdout, (char *)NULL);
		setbuf(stderr, (char *)NULL);
	}

	Py_SetProgramName(argv[0]);
	Py_Initialize();

	if (Py_VerboseFlag)
		fprintf(stderr, "Python %s\n%s\n",
			Py_GetVersion(), Py_GetCopyright());

	PySys_SetArgv(argc, argv);

	n = PyImport_ImportFrozenModule("__main__");
	if (n == 0)
		Py_FatalError("__main__ not frozen");
	if (n < 0) {
		PyErr_Print();
		sts = 1;
	}
	else
		sts = 0;

	if (inspect && isatty((int)fileno(stdin)))
		sts = PyRun_AnyFile(stdin, "<stdin>") != 0;

	Py_Finalize();
	return sts;
}
