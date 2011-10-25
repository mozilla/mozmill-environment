#!/usr/bin/env bash

PWD=$(dirname $0)

# Prepare and change into virtual environment
python -B $PWD/scripts/virtualenv.py $PWD
source $PWD/bin/activate

# install dependencies
easy_install --upgrade pip

# The pip command to not compile binary files does not work. Install it manually.
# pip install --upgrade --global-option="--pure" mercurial
pip install --download=./ mercurial==1.7.3
mkdir mercurial
tar -C mercurial -xvf mercurial*.tar.gz --strip-components=1
cd mercurial
python setup.py --pure install
cd ..
rm -R mercurial*

pip install --upgrade mozmill
