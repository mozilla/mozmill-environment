#!/usr/bin/env bash

TARGET_LOCATION="public_html/downloads/mozmill-env/"

scp *.zip people:$TARGET_LOCATION
rm *.zip
