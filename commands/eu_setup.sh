#!/bin/bash

# check if path to commands is already on the path or not
# only add if it is not

# given argument $1 must be the path to the exputils folder
export EU_COMMANDS_PATH=$1/commands
export EU_PRJ_DEFINITIONS_PATH=$1/projects

# check if commands dir is on PATH, if not then add
if [[ ":$PATH:" != *":$EU_COMMANDS_PATH:"* ]] ; then
    export PATH="$EU_COMMANDS_PATH:$PATH"
fi