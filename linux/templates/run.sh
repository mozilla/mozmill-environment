#!/usr/bin/env bash

# The full path has to be used to source into the environment
ABS_DIR=$(cd $(dirname $BASH_SOURCE); pwd)
COMMAND="source $ABS_DIR/bin/activate"

if [ $# -gt 0 ] ; then
    # Automatic mode: Execute the command as given by parameters
    $COMMAND
    $@
    deactivate
else
    # Interactive mode: Ensure that the script gets sourced
    if [ "$0" = "$BASH_SOURCE" ] ; then
        echo "To activate the interactive shell run '. $BASH_SOURCE'."
        echo
    else
        $COMMAND
        echo "Welcome to the interactive Mozmill shell."
        echo "Run 'mozmill --help' for assistance or 'deactivate' to exit."
        echo
    fi
fi
