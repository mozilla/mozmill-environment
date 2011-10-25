#!/usr/bin/env bash

ENV=mozmill-env
URL=https://bitbucket.org/ianb/virtualenv/raw/tip/virtualenv.py

mkdir $ENV/scripts
curl $URL > $ENV/scripts/virtualenv.py

zip -r9 ../mozmill-$(basename $(pwd)).zip $ENV
rm -R $ENV/scripts
