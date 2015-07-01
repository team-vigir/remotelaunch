#!/bin/bash
# This code will be run in every screen on the remote machine. It is typically
# used to source ros and setup any other environment variables you need.
cmdline=("$@")
if [ $# == 0 ]; then
    cmdline=($SHELL -i)
fi

export VIGIR_ROOT_DIR=/home/user/vigir_repo
echo "sourcing catkin_ws................"
source "/home/user/vigir_repo/catkin_ws/install/setup.bash"
echo "sourcing scripts setup.bash.................."
source "/home/user/vigir_repo/scripts/setup/setup.bash"
shopt -s expand_aliases

exec "${cmdline[@]}"
