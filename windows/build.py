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


base_dir = os.path.abspath(os.path.dirname(__file__))

assets_dir = os.path.join(base_dir, os.path.pardir, 'assets')
template_dir = os.path.join(base_dir, "templates")

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
shutil.rmtree(env_dir, True)

logging.info("Install 'MSYS' in unattended mode. Answer questions with 'y' and 'n'.")
# See: http://www.jrsoftware.org/ishelp/index.php?topic=setupcmdline
msys_file = os.path.join(assets_dir, "msys_setup.exe")
subprocess.check_call([msys_file, '/VERYSILENT', '/SP-', '/NOICONS',
                       '/DIR=%s' % (msys_dir)])

logging.info("Replace MSYS DLLs with memory rebased versions.")
msys_dll_file = os.path.join(assets_dir, 'msys_dll.zip')
msys_dll_zip = zipfile.ZipFile(msys_dll_file, "r")
msys_dll_zip.extractall(os.path.join(msys_dir, 'bin'))
msys_dll_zip.close()

logging.info("Install 'mintty'")
mintty_file = os.path.join(assets_dir, 'msys_mintty.zip')
mintty_zip = zipfile.ZipFile(mintty_file, "r")
mintty_zip.extract("mintty.exe", os.path.join(msys_dir, 'bin'))
mintty_zip.close()

logging.info("Copy template files into environment")
copytree(template_dir, env_dir, True)

logging.info("Copy Python installation (including pythonXX.dll into environment)")
copytree(sys.prefix, os.path.join(env_dir, 'python'), True)
dlls = glob.glob(os.path.join(os.environ['WINDIR'], "system32", "python*.dll"))
for dll_file in dlls:
    shutil.copy(dll_file, python_dir)

logging.info("Creating new virtual environment")
virtualenv_file = os.path.join(assets_dir, 'virtualenv.py')
subprocess.check_call(["python", virtualenv_file, env_dir])

logging.info("Reorganizing folder structure")
shutil.rmtree(os.path.join(python_dir, "Lib", "site-packages"), True)
shutil.move(os.path.join(env_dir, "Lib", "site-packages"),
            os.path.join(python_dir, "Lib"))
shutil.rmtree(os.path.join(env_dir, "Include"), True)
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
target_archive = os.path.join(os.path.dirname(base_dir), "%s-windows" % mozmill_version)
shutil.make_archive(target_archive, "zip", base_dir, os.path.basename(env_dir))

shutil.rmtree(env_dir, True)

logging.info("Successfully created the environment: '%s.zip'", target_archive)
