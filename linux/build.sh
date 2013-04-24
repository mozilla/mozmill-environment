#!/usr/bin/env bash

VERSION_MOZMILL=$1

VERSION_MERCURIAL=2.1
VERSION_MOZDOWNLOAD=1.7
VERSION_PYTHON=$(python -c "import sys;print sys.version[:3]")

ENV_DIR=mozmill-env
TARGET_ARCHIVE=$(dirname $(pwd))/$VERSION_MOZMILL-$(basename $(pwd)).zip


cleanup () {
    echo "Cleaning-up temporary files and folders"
    rm -r $ENV_DIR
}

if [ ! -n "$1" ] ; then
  echo Version of Mozmill to be installed is required as first parameter.
  exit 1
fi

echo "Creating new virtual environment"
python ../assets/virtualenv.py $ENV_DIR

echo "Activating the new environment"
source $ENV_DIR/bin/activate
if [ ! -n "${VIRTUAL_ENV:+1}" ]; then
    echo "### Failure in activating the new virtual environment: '$ENV_DIR'"
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
mv $ENV_DIR/lib/python$VERSION_PYTHON/site-packages/ $ENV_DIR/python-lib

FOLDERS="lib/ include/ python-lib/pip* bin/activate* bin/python* bin/easy_install* bin/pip*"
for folder in $FOLDERS ; do
    rm -r $ENV_DIR/$folder
done

# Remove the local symlink which gets created and doesn't seem to be necessary.
# See: https://github.com/pypa/virtualenv/issues/118
rm -r $ENV_DIR/local

cp -r templates/* $ENV_DIR

echo "Updating scripts for relocation of the environment"
sed -i 's/#!.*/#!\/usr\/bin\/env python/g' $ENV_DIR/bin/*

echo "Deleting pre-compiled Python modules"
find $ENV_DIR/ -name '*.pyc' -exec rm {} \;
find $ENV_DIR/ -name '*.pyo' -exec rm {} \;
find $ENV_DIR/ -name '*.so' -exec rm {} \;

echo "Building zip archive of environment"
zip -r $TARGET_ARCHIVE $ENV_DIR

cleanup

echo "Successfully created the environment: '$TARGET_ARCHIVE'"
