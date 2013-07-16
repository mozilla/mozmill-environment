#!/usr/bin/env bash

# Link to the folder which contains the zip archives of virtualenv
URL_VIRTUALENV=https://codeload.github.com/pypa/virtualenv/zip/

VERSION_PYTHON=$(python -c "import sys;print sys.version[:3]")
VERSION_MOZMILL=$1

VERSION_MERCURIAL=2.6.2
VERSION_MOZDOWNLOAD=1.7.2
VERSION_VIRTUALENV=1.9.1

DIR_BASE=$(cd $(dirname ${BASH_SOURCE}); pwd)
DIR_ENV=${DIR_BASE}/mozmill-env
DIR_TMP=${DIR_BASE}/tmp

TARGET_ARCHIVE=$(dirname $(pwd))/$VERSION_MOZMILL-$(basename $(pwd)).zip


cleanup () {
    echo "Cleaning-up temporary files and folders"
    rm -r $DIR_ENV
    rm -r $DIR_TMP
}

if [ ! -n "$1" ] ; then
  echo Version of Mozmill to be installed is required as first parameter.
  exit 1
fi

echo "Fetching virtualenv ${VERSION_VIRTUALENV} and creating virtual environment"
mkdir ${DIR_TMP}
curl ${URL_VIRTUALENV}${VERSION_VIRTUALENV} > ${DIR_TMP}/virtualenv.zip
unzip ${DIR_TMP}/virtualenv.zip -d ${DIR_TMP}
python ${DIR_TMP}/virtualenv-${VERSION_VIRTUALENV}/virtualenv.py ${DIR_ENV}

echo "Activating the new environment"
source $DIR_ENV/bin/activate
if [ ! -n "${VIRTUAL_ENV:+1}" ]; then
    echo "### Failure in activating the new virtual environment: '$DIR_ENV'"
    cleanup
    exit 1
fi

echo "Installing required Python modules"
pip install --upgrade --global-option="--pure" mercurial==$VERSION_MERCURIAL
pip install --upgrade simplejson

echo "Installing Mozmill $VERSION_MOZMILL and related packages"
pip install --upgrade mozmill==$VERSION_MOZMILL
pip install --upgrade mozdownload==$VERSION_MOZDOWNLOAD

echo "Deactivating the environment"
deactivate

echo "Copying template files and reorganizing folder structure"
mv $DIR_ENV/lib/python$VERSION_PYTHON/site-packages/ $DIR_ENV/python-lib

FOLDERS="lib/ .Python include/ python-lib/pip* bin/activate* bin/python* bin/easy_install* bin/pip*"
for folder in $FOLDERS ; do
    rm -r $DIR_ENV/$folder
done

cp -r templates/ $DIR_ENV

echo "Updating scripts for relocation of the environment"
sed -i '' 's/#!.*/#!\/usr\/bin\/env python/g' $DIR_ENV/bin/*

echo "Deleting pre-compiled Python modules"
find $DIR_ENV/ -name '*.pyc' -exec rm {} \;
find $DIR_ENV/ -name '*.pyo' -exec rm {} \;
find $DIR_ENV/ -name '*.so' -exec rm {} \;

echo "Building zip archive of environment"
zip -FSr $TARGET_ARCHIVE $(basename $DIR_ENV)

cleanup

echo "Successfully created the environment: '$TARGET_ARCHIVE'"
