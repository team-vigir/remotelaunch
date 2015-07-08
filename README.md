# remotelaunch

This repo is meant to be used to help in the launching and deploying of several packages to multiple machines at one time. For this to work properly the user must set the $VIGIR_ROOT_DIR environment variable to the folder containing your catkin workspace so the software can build it and install the made code onto the other machines. The following are the arguments you can pass to the remote launch python script:
remotelaunch.py [-mdls] profile_name user_name profiles_directory_path

profile_name is required and is used to define what gets run and where. The profile consists of a folder that is the profile name and a series of files inside. It is expecting an environment script "env.sh" that is run in each screen before every command to setup whatever environment you need. The other files are files defining the commands to be run on each computer where the file name determines the order and computer name, for example the name for aragorn to run 3rd would be "03_aragorn.sh". 
user_name is an optional field that defaults to vigir if not entered.
profiles_directory_path is an optional field that defaults to "remotelaunch/profiles" if not entered.
-m : Make runs make install on th local repo to generate the code to deploy
-d : Deploy deploys the installed code to all machines listed in the profile specified
-l : Launch executes the commands on the remote machine.
-s : Stop kills all remotelaunch created screens on the remote machines.
