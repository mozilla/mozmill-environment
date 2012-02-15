#!/usr/bin/env python

import fileinput
import glob
import optparse
import os
import subprocess
import shutil
import sys
import urllib
import zipfile


VERSION_MERCURIAL = "2.1"
VERSION_MINTTY = "1.0.1"
VERSION_MSYS = "1.0.11"
VERSION_VIRTUALENV = "1.7"

URL_MSYS = "http://sourceforge.net/projects/mingw/files/MSYS/Base/msys-core/msys-%(VERSION)s/MSYS-%(VERSION)s.exe/download" % { 'VERSION' : VERSION_MSYS }
URL_MINTTY = "http://mintty.googlecode.com/files/mintty-%s-msys.zip" % VERSION_MINTTY
URL_VIRTUALENV = "https://raw.github.com/pypa/virtualenv/%s/virtualenv.py" % VERSION_VIRTUALENV

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "templates")
download_dir = os.path.join(base_dir, "downloads")

env_dir = os.path.join(base_dir, "mozmill-env")
msys_dir = os.path.join(env_dir, "msys")
python_dir = os.path.join(env_dir, "python")

def download(url, filename):
    '''Download a remote file from an URL to the specified local folder.'''

    try:
        urllib.urlretrieve(url, filename)
    except Exception, e:
        print "Failure downloading '%s': %s" % (url, str(e))
        raise


def make_relocatable(filepath):
    '''Remove python path from the Scripts'''

    files = glob.glob(filepath)

    for file in files:
        for line in fileinput.input(file, inplace=1):
            if fileinput.isfirstline() and line.startswith("#!"):
                # Only on Windows we have to set Python into unbuffered mode
                print "#!python -u"
            else:
                print line,

        fileinput.close()


parser = optparse.OptionParser()
(options, args) = parser.parse_args()

if not args:
    parser.error("Version of Mozmill to be installed is required as first parameter.")
mozmill_version = args[0]

print "Delete an already existent environment sub folder"
os.system("del /s /q %s" % (env_dir))

print "Download and install 'MSYS' in unattended mode. Answer questions with 'y' and 'n'."
# See: http://www.jrsoftware.org/ishelp/index.php?topic=setupcmdline
os.system("mkdir %s" % download_dir)
setup_msys = os.path.join(download_dir, "setup_msys.exe")
download(URL_MSYS, setup_msys)
subprocess.check_call([setup_msys, '/VERYSILENT', '/SP-', '/DIR=%s' % (msys_dir),
                       '/NOICONS' ])

print "Download and install 'mintty'"
mintty_path = os.path.join(download_dir, os.path.basename(URL_MINTTY))
download(URL_MINTTY, mintty_path)
zip = zipfile.ZipFile(mintty_path, "r")
zip.extract("mintty.exe", "%s\\bin" % (msys_dir))
zip.close()

print "Copy template files into environment"
os.system("xcopy /S /I /H %s %s" % (template_dir, env_dir))

print "Copy Python installation (including pythonXX.dll into environment"
os.system("xcopy /S /I /H %s %s\\python" % (sys.prefix, env_dir))
os.system("xcopy %s\\system32\\python*.dll %s" % (os.environ['WINDIR'], python_dir))

print "Fetching version %s of virtualenv and creating new environment" % VERSION_VIRTUALENV
virtualenv_path = os.path.join(download_dir, os.path.basename(URL_VIRTUALENV))
download(URL_VIRTUALENV, virtualenv_path)
subprocess.check_call(["python", virtualenv_path, env_dir])

print "Reorganizing folder structure"
os.system("move /y %s\\Scripts %s" % (env_dir, python_dir))
os.system("rd /s /q %s\\Lib\\site-packages" % (python_dir))
os.system("move /y %s\\Lib\\site-packages %s\\Lib" % (env_dir, python_dir))
os.system("rd /s /q %s\\Lib" % (env_dir))
make_relocatable("%s\\Scripts\\*.py" % (python_dir))

print "Installing required Python modules"
subprocess.check_call(["%s\\run.cmd" % env_dir, "pip", "install",
                       "--upgrade", "--global-option='--pure'",
                       "mercurial==%s" % VERSION_MERCURIAL])
subprocess.check_call(["%s\\run.cmd" % env_dir, "pip", "install",
                       "--upgrade", "mozmill==%s" % (mozmill_version)])
make_relocatable("%s\\Scripts\\*.py" % (python_dir))
make_relocatable("%s\\Scripts\\hg" % (python_dir))

print "Deleting easy_install and pip scripts"
os.system("del /q %s\\Scripts\\easy_install*" % (python_dir))
os.system("del /q %s\\Scripts\\pip*" % (python_dir))

print "Deleting pre-compiled Python modules and build folder"
os.system("del /s /q %s\\*.pyc" % (python_dir))
os.system("rd /s /q %s\\build" % (env_dir))

print "Building zip archive of environment"
target_archive = os.path.join(os.path.dirname(base_dir), "%s-win" % mozmill_version)
shutil.make_archive(target_archive, "zip", base_dir, os.path.basename(env_dir))

os.system("rd /s /q %s" % (env_dir))

print "Successfully created the environment: '%s.zip'" % target_archive
