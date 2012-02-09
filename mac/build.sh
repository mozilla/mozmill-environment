#!/usr/bin/env bash

MOZMILL_VERSION=$1

MERCURIAL_VERSION=2.1
PYTHON_VERSION=$(python -c "import sys;print sys.version[:3]")
VIRTUALENV_VERSION=1.5.2

ENV_DIR=mozmill-env
TARGET_ARCHIVE=$(dirname $(pwd))/$MOZMILL_VERSION-$(basename $(pwd)).zip

VIRTUALENV_URL=https://bitbucket.org/ianb/virtualenv/raw/$VIRTUALENV_VERSION/virtualenv.py


cleanup () {
    echo "Cleaning-up temporary files and folders"
    rm -r tmp $ENV_DIR
}

if [ ! -n "$1" ] ; then
  echo Version of Mozmill to be installed is required as first parameter.
  exit 1
fi

echo "Fetching latest version of virtualenv and creating new environment"
mkdir tmp && curl $VIRTUALENV_URL > tmp/virtualenv.py
python tmp/virtualenv.py --no-site-packages $ENV_DIR

echo "Activating the new environment"
source $ENV_DIR/bin/activate
if [ ! -n "${VIRTUAL_ENV:+1}" ]; then
    echo "### Failure in activating the new virtual environment: '$ENV_DIR'"
    cleanup
    exit 1
fi

echo "Installing required Python modules"
pip install --upgrade --global-option="--pure" mercurial==$MERCURIAL_VERSION
pip install --upgrade simplejson

echo "Installing Mozmill $MOZMILL_VERSION"
pip install --upgrade mozmill==$MOZMILL_VERSION

echo "Deactivating the environment"
deactivate

echo "Copying template files and reorganizing folder structure"
mv $ENV_DIR/lib/python$PYTHON_VERSION/site-packages/ $ENV_DIR/python-lib

FOLDERS="lib/ .Python include/ python-lib/pip* bin/activate* bin/python* bin/easy_install* bin/pip*"
for folder in $FOLDERS ; do
    rm -r $ENV_DIR/$folder
done

cp -r templates/ $ENV_DIR

echo "Updating scripts for relocation of the environment"
sed -i '' 's/#!.*/#!\/usr\/bin\/env python/g' $ENV_DIR/bin/*

echo "Deleting pre-compiled Python modules"
find $ENV_DIR/ -name '*.pyc' -exec rm {} \;
find $ENV_DIR/ -name '*.pyo' -exec rm {} \;
find $ENV_DIR/ -name '*.so' -exec rm {} \;

"Building zip archive of environment"
zip -r $TARGET_ARCHIVE $ENV_DIR

cleanup

echo "Successfully created the environment: '$TARGET_ARCHIVE'"