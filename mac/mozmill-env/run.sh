#!/usr/bin/env bash

PWD=$(dirname $0)

# Change into the virtual environment
source $PWD/bin/activate

if [ $# -gt 0 ]; then
   # Execute all command line arguments
   $@
else
   echo "Welcome to Mozmill. Use '$(basename $0) mozmill --help' for assistance."
fi
