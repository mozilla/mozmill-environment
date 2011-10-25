Preparation Steps
=================
Due to missing automation capabilities of the installer files (at least for the
Mercurial module), you are forced to manually setup the python folder.

Follow the steps below to glue all the pieces together:

Software Requirements
---------------------
* Python 2.6.x (http://www.python.org/)
* Python Mercurial 1.7.x for Python 2.6 (http://bitbucket.org/tortoisehg/thg-winbuild/)
* Setuptools for Python 2.6 (http://pypi.python.org/pypi/setuptools)

Steps
-----
1. Install Python 2.6 via "Install just for me" (don't install Tcl/Tk, and Documentation)
2. Install the Python Mercurial module
3. Install the Setuptools
4. Copy the c:\Python26 folder into the python26 subfolder of the Mozmill environment
5. Uninstall each of the installed software from steps 1 - 3 (do it backwards)
