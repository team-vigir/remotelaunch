#!/usr/bin/python3

#/*********************************************************************
# * Software License Agreement (BSD License)
# *
# *  Copyright (c) 2013-2015, TORC Robotics, LLC ( Team ViGIR )
# *  All rights reserved.
# *
# *  Redistribution and use in source and binary forms, with or without
# *  modification, are permitted provided that the following conditions
# *  are met:
# *
# *   * Redistributions of source code must retain the above copyright
# *     notice, this list of conditions and the following disclaimer.
# *   * Redistributions in binary form must reproduce the above
# *     copyright notice, this list of conditions and the following
# *     disclaimer in the documentation and/or other materials provided
# *     with the distribution.
# *   * Neither the name of Team ViGIR, TORC Robotics, nor the names of its
# *     contributors may be used to endorse or promote products derived
# *     from this software without specific prior written permission.
# *
# *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# *  POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************/
# 
# /* Author: David Conner (TORC Robotics) */

import os
from os.path import expanduser, isfile

"""This program uses ssh, rsync, screen and pkill to distribute programs to several hosts and to launch or stop them remotely. If you don't have the necessary programs installed, it will fail horribly. Also, you probably want to setup passwordless ssh key authentication.

There are some options hardcoded inside this script file:
SHARED_DIRECTORY is the path of the shared directory.
SCRIPT_DIRECTORY is the path of the directory that contains the launch scripts.

SCRIPT_DIRECTORY must be inside SHARED_DIRECTORY, otherwise it isn't synced.
Both variables can use ~ as an abreviation for the home directory.
Inside SCRIPT_DIRECTORY are subfolders (called profiles) that contain the launch scripts.
The launch scripts have to be named "[0-9][0-9]_HOSTNAME.sh".
They are executed in alphabetic order on the hostname specified in the file name.
It is not necessary to have consecutive numbering.

A waiting time after the execution of one script can be set by including the line:
#remotelaunch sleep=time_in_seconds
in the script file. This option accepts floats.
"""

ROOT_DIR = os.getenv("VIGIR_ROOT_DIR")
SHARED_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/")
SCRIPT_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
LAUNCH_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
ENV_SCR_PATH = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
RELATIVE_ROOT_PATH = os.path.relpath(ROOT_DIR, os.path.expanduser("~"),)
ROOT_DIR = os.getenv("VIGIR_ROOT_DIR")
SHARED_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/")
SCRIPT_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
LAUNCH_DIRECTORY = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
ENV_SCR_PATH = os.path.join(ROOT_DIR, "scripts", "remotelaunch/profiles/")
RELATIVE_ROOT_PATH = os.path.relpath(ROOT_DIR, os.path.expanduser("~"),)

#users:
DEMO = "demo"
TESTING = "testing"
##

#SSH AUTH VAR
SSH_AUTH = True;

SSHUSER = "demo";
USER_DEFN= False;

DEFAULT_PROFILE = "default"

import subprocess
import os
import glob
import re
import time
import sys
from subprocess import Popen
import pipes

SHARED_DIRECTORY = os.path.expanduser(SHARED_DIRECTORY)
SCRIPT_DIRECTORY = os.path.expanduser(SCRIPT_DIRECTORY)

def getSSH():
    """Method to setup the ssh key"""
    global SSH_AUTH
    #this will setup the ssh-key remembering

    if SSH_AUTH == False:
        home = expanduser("~")
        print( "Add SSH key from "+home+"/.ssh/id_rsa ...")
        subprocess.check_call(["ssh-add", home+"/.ssh/id_rsa"])
        SSH_AUTH = True;

def get_remote_root():
    global SSHUSER
    global RELATIVE_ROOT_PATH
    return os.path.join("/home", SSHUSER, RELATIVE_ROOT_PATH, '')

def check_user():
    """Function to check the profile"""
    global SSHUSER
    global LAUNCH_DIRECTORY
    global ENV_SCR_PATH
    global USER_DEFN
    global RELATIVE_ROOT_PATH

    if USER_DEFN == False:
        SSHUSER = args.user
        profile = args.profile

        vig = get_remote_root()
#        LAUNCH_DIRECTORY = os.path.join(vig, "scripts/remotelaunch/profiles/")
#        ENV_SCR_PATH = os.path.join(vig, "scripts/remotelaunch/profiles/" + profile + "/env.sh");
        USER_DEFN = True;
        print("Running with user: " + SSHUSER)
        print("  profile: " + profile)
        print("  remote root: "+vig)
        print("  Launch directory: "+LAUNCH_DIRECTORY)
        print("  Path to env.sh: "+ENV_SCR_PATH)


def make_destination():
    """Function to make the testing install in /home/testing/ or /home/demo/. This is the install that will be copied."""
    global SSHUSER

    returncode = 0
    """ Make sure the installation is up to date """
    print( "Clean the behaviors system of temp files ..." )
    returncode = subprocess.call("rosrun vigir_be_widget clear_cache",shell=True)
    if returncode:
        print("Error in executing rosrun vigir_be_widget clear_cache for remote launch!");
        print("    returncode="+str(returncode))
        return False

    print( "Delete the install folder to prevent stray behavior temp files ..." )
    RM_INSTALL_DIR  = "rm -rf ~/vigir_repo/catkin_ws/install"
    print(RM_INSTALL_DIR)
    returncode = subprocess.call(RM_INSTALL_DIR,shell=True)
    if returncode:
        print("Error in deleting the catkin_ws/install directory!");
        print("    returncode="+str(returncode))
        return False

    """ Make sure the installation is up to date """
    print( "Build and install the latest system ..." )
    returncode = subprocess.call("vigir_make"+" --install",shell=True)
    if returncode:
        print("Error in executing vigir_make --install for remote launch!");
        print("    returncode="+str(returncode))
        return False
    else:
        print("Completed installation of Team ViGIR software!")

    print("  Now make deployment ...")

    #make the neccessary dirs:
    VIGIR_REPO = get_remote_root()
    print("  remote root: "+VIGIR_REPO)

    checkpath  = os.path.join(VIGIR_REPO, "made_by_RL.txt")
    checkexist = os.path.join(VIGIR_REPO, "catkin_ws/install/setup.bash")

    if not os.path.isfile(checkexist):
        print('\033[94m'+'  No repo located at '+VIGIR_REPO+'\033[0m')
        print('\033[92m'+"  Creating new deployment at"+VIGIR_REPO+'\033[0m')
        returncode = subprocess.call(["/usr/bin/sudo", "./make_destination.sh", SSHUSER, ])
        if returncode:
            print("    returncode="+str(returncode))
            return False
        else:
            return True
    elif os.path.isfile(checkpath):
        print('\033[92m'+"  Updating the existing remote deployment repo at "+VIGIR_REPO+'\033[0m')
        returncode = subprocess.call(["/usr/bin/sudo", "./make_destination.sh", SSHUSER])
        if returncode:
            print("    returncode="+str(returncode))
            return False
        else:
      	    return True
    else:
        print('\033[91m'+"  Not creating repo because the existing repo was not created by Remote Launch."+'\033[0m')
        returncode = -1
        return False

def get_hostname(script):
    """Returns the hostname from the name of a launch script."""
    mo = re.match("[0-9][0-9]_(.*).sh", os.path.basename(script))
    if mo:
    #the .* i.e host name
        return mo.group(1)
    return False

def detect_hosts(configuration):
    """Returns a list of hosts that is generated from the names of the launch scripts in a profile subdirectory."""
    pattern = os.path.join(SCRIPT_DIRECTORY, configuration, "[0-9][0-9]_*.sh")
    hosts = {}
    for script in glob.glob(pattern):
        host = get_hostname(script)
        if host:
            hosts[host] = True
    return hosts.keys()

def list_profiles():
    """List all profiles in the SCRIPT_DIRECTORY."""
    marker = {True: "(*)", False: "   "}
    print("  Available profiles:")
    for profile in os.listdir(SCRIPT_DIRECTORY):
        print("  {} {}".format(marker[profile == DEFAULT_PROFILE], profile))


def exists_remote(host, path):
	proc = subprocess.Popen(['ssh', host, 'test -f %s' % pipes.quote(path)])
	proc.wait()
	return proc.returncode == 0

def check_deploy(target):

    """Use rsync to push the SHARED_DIRECTORY to a target host."""
    #make the neccessary dirs:
    VIGIR_REPO = get_remote_root()
    remote = "{}@{}:{}".format(SSHUSER, target, VIGIR_REPO)

    print("  check deployment at remote: "+remote)

    checkpath = os.path.join(VIGIR_REPO, "made_by_RL.txt")
    checkexist = os.path.join(VIGIR_REPO, "catkin_ws/install/setup.bash")
    checkremote = "{}@{}".format(SSHUSER, target)

    if not exists_remote(checkremote, checkexist):
        print('     No existing repo located on {}'.format(target))
        return True
    elif exists_remote(checkremote, checkpath):
        return True
    else:
        #" Not valid for deployment"
        print('\033[91m'+"  Cannot deploy to {} because existing files were not created by Remote Launch!".format(target)+'\033[0m')
        print("     "+remote)
        return False



def deploy(target):

    """Use rsync to push the SHARED_DIRECTORY to a target host."""
    #make the neccessary dirs:
    VIGIR_REPO = get_remote_root()
    # target_base = os.path.abspath(VIGIR_REPO+"/..")
    remote = "{}@{}:{}".format(SSHUSER, target, VIGIR_REPO)
    if check_deploy(target):
        print('\033[92m'+"  Deploying data to {}.".format(target)+"..."+'\033[0m')
        print("    from : "+VIGIR_REPO)
        print("    to   : "+remote)
        try:
          subprocess.check_call(["rsync", "--delete", "-rlpgoDze", "ssh", VIGIR_REPO, remote])
          return True
        except:
            print("Failed to deploy to "+remote)
            return False
    else:
        print('\033[91m'+"  Not deploying to {} because existing files were not created by Remote Launch!".format(target)+'\033[0m')
        print("     "+remote)
        return False

def stop(target):
    """Use pkill to stop all screen sessions on a target host that have a name that contains remotelaunch."""
    print('\033[93m'+"  Stopping scripts on {}..".format(target)+'\033[0m')
    execute_remote(target, "pkill -f remote_launch")

    return True

def kill_with_fire(target):
    """Use pkill to stop all screen sessions on a target host that have a name that contains remotelaunch."""
    print('\033[93m'+"  Killing scripts on {}.with fire!..".format(target)+'\033[0m')
    execute_remote(target, "pkill -9 -f remote_launch")

    return True

def wipe_screen(target):
    """Wipe potentially dead screens after kill."""
    print('\033[93m'+"  Wiping any dead screens on {}.with fire!..".format(target)+'\033[0m')
    execute_remote_in_screen(target, "screen -wipe")

    return True
def cmd_all(function, profile):
    """Determine the host names and run a function for each host for a given profile."""
    ret=True
    for host in detect_hosts(profile):
        ret = ret and function(host)
    return ret

def execute_remote(target, command):
  """Execute a command on a remote host via ssh."""
  try:
    if subprocess.check_call(["ssh", "{}@{}".format(SSHUSER, target), "{}".format(command)]):
        return False
    else:
        return True
  except:
    print("Failed to start subprocess on "+target)
    print("  Abort: "+command)
    return False

    #Popen("ssh {}@{} bash -i {}".format(SSHUSER, target, command), shell=True)

def execute_remote_in_screen(target, command, suffix=''):
    """Execute a command in a new screen session on a remote host via ssh."""
    ret = execute_remote(target, "screen -dmS remote_launch{} {}".format(suffix, command))

    if ret:
      if "roscore" in command:
        print("Start roscore and wait for response ...")
        wait_for_roscore = True
        while wait_for_roscore:
            returncode = subprocess.call("rostopic list > /dev/null 2> /dev/null",shell=True)
            if returncode == 0:
               print("  roscore is online!")
               wait_for_roscore = False
            else:
                time.sleep(1.0)
                print("  Waiting for roscore ...")

    return ret

def launch_all(profile):
    """Run all launch scripts on the corresponding remote hosts."""
    ret = True
 #   global LAUNCH_DIRECTORY
    pattern = os.path.join(LAUNCH_DIRECTORY, profile, "[0-9][0-9]_*.sh")
    print(pattern)
    for index, script in enumerate(sorted(glob.glob(pattern))):
        target = get_hostname(script)
        if not target:
            print('\033[91m'+"Could not determine hostname from script file name."+'\033[0m')
            sys.exit(1)
        print("  Running {} on {}.".format(script, target))
        #parse options:
        sleeptime = False
        with open(script, "r") as script_:
            temp_count = 0
            for line in script_.readlines():
                m_ = re.match(r"#remotelaunch\s*sleep=([.0-9]*)", line)
                c_ = re.match(r"^\#.*", line)

                #print( "COUNT : {}".format(temp_count) )

                if m_:
                    sleeptime = float(m_.group(1))
                    print( "    " + str(temp_count) + ' : ' + target + ' : ' + line.rstrip('\n')  )
                    time.sleep(sleeptime)
                elif c_:
                    print( "    " + str(temp_count) + ' : ' + target + ' : ' + '  Ignoring Comment' )
                else:
                    print("    " + str(temp_count) + ' : ' + target + ' : ' + line.rstrip('\n') )
                    ret = ret and execute_remote_in_screen(target, "{} {}".format(ENV_SCR_PATH, line), suffix=temp_count)

                temp_count+=1 # track the line indices used in remote launch names

    return ret

def stop_all(profile):
    print('\033[92m'+"Stop processes on the following remote machines!"+'\033[0m')
    print('  '+str(list(detect_hosts(profile))))
    if cmd_all(stop, profile):
        print('\033[92m'+"Successfully stopped remote launch on all remote machines!"+'\033[0m')
    else:
        print('\033[91m'+"Failed to stop remote launch on all remote machines - halt deployment!"+'\033[0m')
        sys.exit(1)

def kill_all(profile):
    print('\033[92m'+"Kill processes on the following remote machines!"+'\033[0m')
    print('  '+str(list(detect_hosts(profile))))
    if cmd_all(kill_with_fire, profile):
        print('\033[92m'+"Successfully stopped remote launch on all remote machines!"+'\033[0m')
    else:
        print('\033[91m'+"Failed to stop remote launch on all remote machines - halt deployment!"+'\033[0m')
        sys.exit(1)

def wipe_all(profile):
    print('\033[92m'+"Wipe dead screens on remote machines!"+'\033[0m')
    print('  '+str(list(detect_hosts(profile))))
    if cmd_all(wipe_screen, profile):
        print('\033[92m'+"Successfully wiped all screens on all remote machines!"+'\033[0m')
    else:
        print('\033[91m'+"Failed to wipe remote launch on all remote machines - halt deployment!"+'\033[0m')
        sys.exit(1)


if __name__ == "__main__":
    if not SHARED_DIRECTORY.endswith("/"):
        print('\033[91m'+"SHARED_DIRECTORY has to end with a slash!"+'\033[0m')
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description = "Deploy, launch and stop programs remotely.", epilog=__doc__)
    parser.add_argument("profile", default="default", nargs="?", help="profile to use; defaults to '{}'".format(DEFAULT_PROFILE))
    parser.add_argument("user", default="testing", nargs="?", help="profile to use; defaults to '{}'".format(DEFAULT_PROFILE))
    parser.add_argument("-d", "--deploy", action="store_true", help="deploy data using rsync")
    parser.add_argument("-l", "--launch", action="store_true", help="launch remote scripts")
    parser.add_argument("-s", "--stop", action="store_true", help="stop remote scripts")
    parser.add_argument("-dl", "--deploylaunch", action="store_true", help="deploy using rsync and then launch remote scripts")
    parser.add_argument("-m", "--make_install", action="store_true", help="make the installation to be deployed")
    parser.add_argument("-mdl", "--makeDeployLaunch", action="store_true", help="make, deploy, and launch")
    parser.add_argument("-md", "--makeDeploy", action="store_true", help="make and deploy")
    parser.add_argument("-p", "--printProfiles", action="store_true", help="print a list of available profiles; the default profile is marked by an asterisk")
    parser.add_argument("directory", default="/scripts/remotelaunch/profiles", nargs="?", help="full path to profiles directory; defaults to '{}'".format(DEFAULT_PROFILE))
    args = parser.parse_args()

    SHARED_DIRECTORY = os.path.join(ROOT_DIR, args.directory)
    (SHARED_DIRECTORY,temp) = os.path.split(SHARED_DIRECTORY)
    SCRIPT_DIRECTORY = os.path.join(ROOT_DIR, args.directory)
    LAUNCH_DIRECTORY = os.path.join(ROOT_DIR, args.directory)
    ENV_SCR_PATH = os.path.join(ROOT_DIR, args.directory, args.profile, "env.sh")
    print(ENV_SCR_PATH)
    if (args.launch or args.deploylaunch) and args.stop:
        print('\033[91m'+"Do you even know what you want to do?"+'\033[0m')
        sys.exit(1)
    if not args.profile in os.listdir(SCRIPT_DIRECTORY):
        print('\033[91m'+"Profile {} not found.".format(args.profile)+'\033[0m')
        list_profiles()
        sys.exit(1)
    if args.make_install or args.makeDeployLaunch or args.makeDeploy:
        check_user()
        if make_destination():
            print('\033[92m'+"Successfully made the deployment repo!"+'\033[0m')
        else:
            print('\033[91m'+"Failed to make the deployment repo - halt deployment!"+'\033[0m')
            sys.exit(1)

    if args.deploy or args.deploylaunch or args.makeDeployLaunch or args.makeDeploy:
        check_user()
        getSSH()

        # Test for valid deployment location for all remotes first before wasting rsync time
        print('\033[92m'+"Check deployment location for the following remote machines ..."+'\033[0m')
        print('  '+str(list(detect_hosts(args.profile))))

        if cmd_all(check_deploy, args.profile):
            print('\033[92m'+"All valid! Now deploy to all of the remote machines ..."+'\033[0m')
        else:
            print('\033[91m'+"Failed to deploy to all remote machines - halt deployment!"+'\033[0m')
            sys.exit(1)

        # If all check out, then deploy to each one
        if cmd_all(deploy, args.profile):
            print('\033[92m'+"Successfully deployed system to remote machines!"+'\033[0m')
        else:
            print('\033[91m'+"Failed to deploy to all remote machines - halt deployment!"+'\033[0m')
            sys.exit(1)

    if args.launch or args.deploylaunch or args.makeDeployLaunch:
        check_user()
        getSSH()
        print('\033[92m'+"First stop any active processes on the following remote machines!"+'\033[0m')
        stop_all(args.profile)
        print('\033[92m'+"  No really ... kill them with fire!"+'\033[0m')
        kill_all(args.profile)
        print('\033[92m'+"  Clean up on aisle 3!"+'\033[0m')
        wipe_all(args.profile)
        print('')
        print('\033[92m'+"Launch processes on the following remote machines!"+'\033[0m')
        print('  '+str(list(detect_hosts(args.profile))))
        if launch_all(args.profile):
            print('\033[92m'+"Successfully launched system on all remote machines!"+'\033[0m')
        else:
            print('\033[91m'+"Failed to launch on all remote machines - halt deployment!"+'\033[0m')
            sys.exit(1)

    if args.stop:
        check_user()
        getSSH()
        stop_all(args.profile)
        print('\033[92m'+"  No really ... kill them with fire!"+'\033[0m')
        kill_all(args.profile)
        print('\033[92m'+"  Clean up on aisle 3!"+'\033[0m')
        wipe_all(args.profile)

    if args.printProfiles:
        list_profiles()

    print('\033[92m'+"Done remote launch!"+'\033[0m')
