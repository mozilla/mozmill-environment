#!/usr/bin/env python

import ctypes
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

# Link to the folder which contains the zip archives of virtualenv
URL_VIRTUALENV = 'https://codeload.github.com/pypa/virtualenv/zip/'

VERSION_MERCURIAL = "2.6.2"
VERSION_MOZDOWNLOAD = "1.9"
VERSION_VIRTUALENV = '1.9.1'

dir_base = os.path.abspath(os.path.dirname(__file__))
dir_assets = os.path.join(dir_base, os.path.pardir, 'assets')
dir_env = os.path.join(dir_base, "mozmill-env")
dir_msys = os.path.join(dir_env, "msys")
dir_python = os.path.join(dir_env, "python")
dir_tmp=os.path.join(dir_base, "tmp")
dir_template = os.path.join(dir_base, "templates")


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


def download(url, target):
    """Downloads the specified url to the given target"""

    response = urllib2.urlopen(url)
    with open(target, 'wb') as f:
        f.write(response.read())

    return target


def remove_files(dir_base, pattern):
    '''Removes all the files matching the given pattern recursively.'''
    files = [os.path.join(root, filename)
             for root, dirnames, filenames in os.walk(dir_base)
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


def main():
    logging.basicConfig(level=logging.INFO)

    parser = optparse.OptionParser()
    (options, args) = parser.parse_args()

    if not ctypes.windll.shell32.IsUserAnAdmin():
        logging.error("Sorry, this script requires administrative privileges.")
        sys.exit(126)

    if not args:
        parser.error("Version of Mozmill-Automation to be installed is required as first parameter.")
    mozmill_automation_version = args[0]

    logging.info("Delete all possible existent folders")
    shutil.rmtree(dir_env, True)

    # Ensure we have a clean and existent temporary directory
    shutil.rmtree(dir_tmp, True)
    os.makedirs(dir_tmp)

    logging.info('Downloading virtualenv %s' % VERSION_VIRTUALENV)
    virtualenv_file = download(URL_VIRTUALENV + VERSION_VIRTUALENV,
                               os.path.join(dir_tmp, 'virtualenv.zip'))
    virtualenv_zip = zipfile.ZipFile(virtualenv_file)
    virtualenv_zip.extractall(dir_tmp)
    virtualenv_zip.close()

    logging.info("Creating new virtual environment")
    virtualenv_script = os.path.join(dir_tmp,
                                     'virtualenv-%s' % VERSION_VIRTUALENV,
                                     'virtualenv.py')
    subprocess.check_call(["python", virtualenv_script, dir_env])

    logging.info("Install 'MSYS' in unattended mode. Answer questions with 'y' and 'n'.")
    # See: http://www.jrsoftware.org/ishelp/index.php?topic=setupcmdline
    msys_file = os.path.join(dir_assets, "msys_setup.exe")
    subprocess.check_call([msys_file, '/VERYSILENT', '/SP-', '/NOICONS',
                           '/DIR=%s' % (dir_msys)])

    logging.info("Replace MSYS DLLs with memory rebased versions.")
    msys_dll_file = os.path.join(dir_assets, 'msys_dll.zip')
    msys_dll_zip = zipfile.ZipFile(msys_dll_file, "r")
    msys_dll_zip.extractall(os.path.join(dir_msys, 'bin'))
    msys_dll_zip.close()

    logging.info("Install 'mintty'")
    mintty_file = os.path.join(dir_assets, 'msys_mintty.zip')
    mintty_zip = zipfile.ZipFile(mintty_file, "r")
    mintty_zip.extract("mintty.exe", os.path.join(dir_msys, 'bin'))
    mintty_zip.close()

    logging.info("Copy template files into environment")
    copytree(dir_template, dir_env, True)

    logging.info("Copy Python installation (including pythonXX.dll into environment)")
    copytree(sys.prefix, os.path.join(dir_env, 'python'), True)
    dlls = glob.glob(os.path.join(os.environ['WINDIR'], "system32", "python*.dll"))
    for dll_file in dlls:
        shutil.copy(dll_file, dir_python)

    logging.info("Reorganizing folder structure")
    shutil.rmtree(os.path.join(dir_python, "Lib", "site-packages"), True)
    shutil.move(os.path.join(dir_env, "Lib", "site-packages"),
                os.path.join(dir_python, "Lib"))
    shutil.rmtree(os.path.join(dir_env, "Include"), True)
    shutil.rmtree(os.path.join(dir_env, "Lib"), True)
    python_scripts_dir = os.path.join(dir_python, "Scripts")
    copytree(os.path.join(dir_env, "Scripts"), python_scripts_dir)
    shutil.rmtree(os.path.join(dir_env, "Scripts"))
    make_relocatable(os.path.join(python_scripts_dir, "*.py"))

    run_cmd_path = os.path.join(dir_env, "run.cmd")

    logging.info("Pre-installing mercurial %s in pure mode" % VERSION_MERCURIAL)
    subprocess.check_call([run_cmd_path, "pip", "install",
                           "--upgrade", "--global-option='--pure'",
                           "mercurial==%s" % VERSION_MERCURIAL])

    logging.info("Installing mozmill-automation %s and related packages" % mozmill_automation_version)
    subprocess.check_call([run_cmd_path, "pip", "install",
                           "--upgrade", "mozmill-automation==%s" %
                               mozmill_automation_version])

    make_relocatable(os.path.join(python_scripts_dir, "*.py"))
    make_relocatable(os.path.join(python_scripts_dir, "hg"))

    logging.info("Deleting easy_install and pip scripts")
    for pattern in ('easy_install*', 'pip*'):
        remove_files(python_scripts_dir, pattern)

    logging.info("Deleting pre-compiled Python modules and build folder")
    remove_files(dir_python, "*.pyc")
    shutil.rmtree(os.path.join(dir_env, "build"), True)

    logging.info("Building zip archive of environment")
    target_archive = os.path.join(os.path.dirname(dir_base), "%s-windows" % mozmill_automation_version)
    shutil.make_archive(target_archive, "zip", dir_base, os.path.basename(dir_env))

    shutil.rmtree(dir_env, True)
    shutil.rmtree(dir_tmp, True)

    logging.info("Successfully created the environment: '%s.zip'", target_archive)

if __name__ == "__main__":
    main()
