#!/bin/bash

#This variable will represent the location of my vigir_repo directory (root of the vigir filesystem) on the new user's filesystem
eval HOME_DIR="~/vigir_repo"
DEST_DIR="/home/$1/vigir_repo"
REMOTE_DIR="$2"

#if this directory already exits, then delete it.
if [ -d "$DEST_DIR" ]; then
	#remove the directory
	rm -rf $DEST_DIR
fi

CURRENT=$PWD

#make the directory new:
mkdir $DEST_DIR
cd $DEST_DIR
#mkdir catkin_ws
mkdir catkin_ws

# #copy over the rosbuild ws
# echo '   copying rosbuild...'
# cp -r $HOME_DIR/rosbuild_ws $DEST_DIR/rosbuild_ws/
# #change setup.sh in rosbuild ws:
# sed -i -e "s?$HOME_DIR?$DEST_DIR?g" $DEST_DIR/rosbuild_ws/setup.sh
# #change the rosinstall:
# sed -i -e "s?$HOME_DIR?$DEST_DIR?g" $DEST_DIR/rosbuild_ws/.rosinstall
# #do not change from devel to install so it will use the source files.
# sed -i -e "s?devel?install?g" $DEST_DIR/rosbuild_ws/.rosinstall

#copy over neccessary items from catkin ws
echo '   copying catkin ...'
cp -r $HOME_DIR/catkin_ws/install $DEST_DIR/catkin_ws/install/
cp -r $HOME_DIR/catkin_ws/external $DEST_DIR/catkin_ws/external/

echo '   copying FlexBE ...'
cp -r $HOME_DIR/catkin_ws/src/vigir_smach_engine/FlexBE $DEST_DIR/

if [ -d "$HOME_DIR/pronto-distro" ]; then
echo '   copying pronto ...'
cp -r $HOME_DIR/pronto-distro $DEST_DIR
cd $DEST_DIR/pronto-distro/pronto-lcm-ros-translators/devel
sed -i -e "s?$HOME_DIR?$DEST_DIR?g" setup.sh
sed -i -e "s?$HOME_DIR?$DEST_DIR?g" _setup_util.py
cd $DEST_DIR
else
echo '   Pronto is not built here!'
fi

echo '   Copying remotelauch files ...'
cp -r $REMOTE_DIR $REMOTE_DIR 

#echo '   copying the libsbpl.so to install/lib ...'
#cp $HOME_DIR/catkin_ws/src/external/sbpl/build/libsbpl.so $DEST_DIR/catkin_ws/install/lib

#change setup.sh in catkin/install:
echo '   modifying catkin setup ...'
sed -i -e "s?$HOME_DIR?$DEST_DIR?g" $DEST_DIR/catkin_ws/install/setup.sh
sed -i -e "s?$HOME_DIR?$DEST_DIR?g" $DEST_DIR/catkin_ws/install/.rosinstall
sed -i -e "s?$HOME_DIR?$DEST_DIR?g" $DEST_DIR/catkin_ws/install/_setup_util.py
sed -i -e "s?devel?install?g"       $DEST_DIR/catkin_ws/install/_setup_util.py


#copy overs scripts folder
echo '   copying scripts...'
cp -r $HOME_DIR/scripts $DEST_DIR/scripts/

# Change to deployment directory
cd $DEST_DIR
#pwd
echo '   Changing library setup files ...'
find . -name *.pc -print | xargs sed -i -e "s?$HOME_DIR?$DEST_DIR?g"

# In this case, the cmake won't be valid without source, but neither will they point to potential different code
echo '   Changing cmake files ...'
find . -name *.cmake -print | xargs sed -i -e "s?$HOME_DIR?$DEST_DIR?g"

#echo '   Removing compiled python ...'
#find . -name *.pyc -print | xargs rm

# cd rosbuild_ws
# echo '   Changing rosbuild make files ...'
# find . -name *.make -print | xargs sed -i -e "s?$HOME_DIR?$DEST_DIR?g"
# 
# echo '   Removing rosbuild compiled object files ...'
# find . -name *.o -print | xargs rm

cd $CURRENT
#pwd

#give everyone access to the folder.
chown -R $1 $DEST_DIR
chmod -R a+xwr $DEST_DIR

# Flag that we made this directory
NOW=$(date)
echo "Created by Team ViGIR remotelaunch script on "$NOW > $DEST_DIR/made_by_RL.txt

echo 'done'
