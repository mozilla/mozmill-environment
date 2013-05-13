#!/usr/bin/env bash

HOST="mozqa"
TARGET_LOCATION="/data/www/mozqa.com/mozmill-env/"

echo "Uploading files ..."
scp *.zip $HOST:$TARGET_LOCATION

echo "Updating folder and file permissions..."
ssh $HOST "sudo /usr/local/sbin/puppetctl run"
