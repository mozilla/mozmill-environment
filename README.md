# Mozmill Environment
The Mozmill environment provides a pre-configured environment for Python with a
full set of tools necessary to run Mozmill tests for Firefox.

## How to build
To build the environment for a given platform change into the appropriate sub
folder and execute the build command.

### Windows
Due to missing automation capabilities of the installer files (at least for the
Python installer), you are forced to manually setup the python installation.

Follow the steps below to glue all the pieces together:

#### Software Requirements
* [Python 2.7.x](http://www.python.org/download/)

#### Steps
1. Install Python: "msiexec /i python-2.7.2.msi /passive ADDLOCAL=Extensions ALLUSERS=1"
2. Execute the 'build.py' script with the version of Mozmill as parameter
3. Answer the questions of the MSYS installer with 'y' and 'n'.
4. Uninstall Python: "msiexec /x python-2.7.2.msi /passive"

## Assets
We don't want to be dependent on the download of external tools and rebasing the
base address of the MSYS DLL files. So all required tools have been made available
in the assets folder.

### MSYS
Version: 1.0.11
URL: http://sourceforge.net/projects/mingw/files/MSYS/Base/msys-core/msys-1.0.11/MSYS-1.0.11.exe/download
File: assets/msys_setup.exe
Rebased DLLs: assets/msys_dll.zip

See Mozilla Build for more information:
http://hg.mozilla.org/mozilla-build/file/a1bc3aa272a8/packageit-msys.sh#l66

### mintty
Version: 1.0.1
URL: http://mintty.googlecode.com/files/mintty-1.0.1-msys.zip
File: msys_mintty.zip

### Virtualenv
Version: 1.7.0
URL: https://raw.github.com/pypa/virtualenv/1.7/virtualenv.py
File: assets/virtualenv.py
