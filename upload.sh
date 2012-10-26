#!/usr/bin/env bash

TARGET_LOCATION="/var/www/html/mozmill-env/"

scp *.zip mozqa:$TARGET_LOCATION
rm *.zip
