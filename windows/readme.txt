Preparation Steps
=================
Due to missing automation capabilities of the installer files (at least for the
Python installer), you are forced to manually setup the python folder.

Follow the steps below to glue all the pieces together:

Software Requirements
---------------------
* Python 2.7.x (http://www.python.org/download/)

Steps
-----
1. Install Python: "msiexec /i python-2.7.2.msi /passive ADDLOCAL=Extensions ALLUSERS=1"
2. Execute the 'build.py' script with the version of Mozmill as first parameter
3. Answer the questions of the MSYS installer with 'y' and 'n'.
4. Uninstall Python: "msiexec /x python-2.7.2.msi /passive"