#!/usr/bin/env python

import fileinput
import fnmatch
import glob
import logging
import optparse
import os
import subprocess
import shutil
import sys
import urllib2
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

logging.basicConfig(level=logging.INFO)

def copytree(src, dst, symlinks=False, ignore=None):
    """
    Copy of shutil.copytree with proper exception handling when the target
    directory exists. (a simple try-except block addition)
    """
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    try:
        os.makedirs(dst)
    except:
        pass

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                shutil.copy2(srcname, dstname)
                # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except EnvironmentError, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise EnvironmentError(errors)


def remove_files(base_dir, pattern):
    '''Removes all the files matching the given pattern recursively.'''
    files = [os.path.join(root, filename)
             for root, dirnames, filenames in os.walk(base_dir)
                for filename in fnmatch.filter(filenames, pattern)]

    for a_file in files:
        os.remove(a_file)


def download(url, filename):
    '''Download a remote file from an URL to the specified local folder.'''

    try:
        req = urllib2.urlopen(url)
        with open(filename, 'wb') as fp:
            shutil.copyfileobj(req, fp)
    except urllib2.URLError, e:
        logging.critical("Failure downloading '%s': %s", url, str(e))
        raise e


def make_relocatable(filepath):
    '''Remove python path from the Scripts'''

    files = glob.glob(filepath)
    for a_file in files:
        for line in fileinput.input(a_file, inplace=1):
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

logging.info("Delete all possible existent folders")
for directory in (download_dir, env_dir, msys_dir):
    shutil.rmtree(directory, True)

logging.info("Download and install 'MSYS' in unattended mode. Answer questions with 'y' and 'n'.")
# See: http://www.jrsoftware.org/ishelp/index.php?topic=setupcmdline
os.mkdir(download_dir)
setup_msys = os.path.join(download_dir, "setup_msys.exe")
download(URL_MSYS, setup_msys)
subprocess.check_call([setup_msys, '/VERYSILENT', '/SP-', '/DIR=%s' % (msys_dir),
                       '/NOICONS'])

logging.info("Download and install 'mintty'")
mintty_path = os.path.join(download_dir, os.path.basename(URL_MINTTY))
download(URL_MINTTY, mintty_path)
mintty_zip = zipfile.ZipFile(mintty_path, "r")
mintty_zip.extract("mintty.exe", os.path.join(msys_dir, 'bin'))
mintty_zip.close()

logging.info("Copy template files into environment")
copytree(template_dir, env_dir, True)

logging.info("Copy Python installation (including pythonXX.dll into environment)")
copytree(sys.prefix, os.path.join(env_dir, 'python'), True)
dlls = glob.glob(os.path.join(os.environ['WINDIR'], "system32", "python*.dll"))
for dll_file in dlls:
    shutil.copy(dll_file, python_dir)

logging.info("Fetching version %s of virtualenv and creating new environment", VERSION_VIRTUALENV)
virtualenv_path = os.path.join(download_dir, os.path.basename(URL_VIRTUALENV))
download(URL_VIRTUALENV, virtualenv_path)
subprocess.check_call(["python", virtualenv_path, env_dir])

logging.info("Reorganizing folder structure")
shutil.rmtree(os.path.join(python_dir, "Lib", "site-packages"), True)
shutil.move(os.path.join(env_dir, "Lib", "site-packages"),
            os.path.join(python_dir, "Lib"))
shutil.rmtree(os.path.join(env_dir, "Lib"), True)
python_scripts_dir = os.path.join(python_dir, "Scripts")
copytree(os.path.join(env_dir, "Scripts"), python_scripts_dir)
shutil.rmtree(os.path.join(env_dir, "Scripts"))
make_relocatable(os.path.join(python_scripts_dir, "*.py"))

logging.info("Installing required Python modules")
run_cmd_path = os.path.join(env_dir, "run.cmd")
subprocess.check_call([run_cmd_path, "pip", "install",
                       "--upgrade", "--global-option='--pure'",
                       "mercurial==%s" % VERSION_MERCURIAL])
subprocess.check_call([run_cmd_path, "pip", "install",
                       "--upgrade", "mozmill==%s" % (mozmill_version)])
make_relocatable(os.path.join(python_scripts_dir, "*.py"))
make_relocatable(os.path.join(python_scripts_dir, "hg"))

logging.info("Deleting easy_install and pip scripts")
for pattern in ('easy_install*', 'pip*'):
    remove_files(python_scripts_dir, pattern)

logging.info("Deleting pre-compiled Python modules and build folder")
remove_files(python_dir, "*.pyc")
shutil.rmtree(os.path.join(env_dir, "build"), True)

logging.info("Building zip archive of environment")
target_archive = os.path.join(os.path.dirname(base_dir), "%s-win" % mozmill_version)
shutil.make_archive(target_archive, "zip", base_dir, os.path.basename(env_dir))

shutil.rmtree(env_dir, True)

logging.info("Successfully created the environment: '%s.zip'", target_archive)
