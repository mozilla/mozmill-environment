#!/usr/bin/env bash

ENV=mozmill-env
PYTHON=$ENV/python26

# Delete left-over files from the installation process
rm -f $PYTHON/Remove*.exe
rm -f $PYTHON/*.log

# Delete pre-compiled scripts
find $PYTHON -name \*.pyc -exec rm {} \;
find $PYTHON -name \*.pyo -exec rm {} \;

zip -r9 ../mozmill-$(basename $(pwd)).zip $ENV
