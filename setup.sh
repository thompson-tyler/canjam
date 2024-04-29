#!/bin/sh

# Detect OS version and install FluidSynth with appropriate
# package manager
OS=$(uname -s)

case ${OS} in
    Darwin*)
    # Mac, check for homebrew or macports
    if [ -d "/opt/homebrew/" ] then
        sudo brew install fluidsynth
    elif [ -d "/opt/local" ] then
        sudo port install fluidsynth
    else
        echo "No package manager found for Mac."
    fi
    ;;

    Linux*)
    # Linux, check for package manager
    if [ -d "/opt/rh" ] then
        # RedHat (Halligan) 
        yum install fluidsynth
    if [ -d " /etc/os-release" ] then
        # Ubuntu or Debian
        sudo apt-get install fluidsynth
    elif [ -d "/etc/fedora-release" ] then
        # Fedora
        sudo dnf install fluidsynth
    else
        echo "No package manager found for ${OS}."
    fi
    ;;
   
    CYGWIN*)
    echo "No thank you!"
    ;;
    *)
    echo "Unknown operating system: ${OS}."
    ;;
esac

# Then, create a Python virtual environment to install packages
python3 -m venv ./canjamvenv
source canjamvenv/bin/activate

pip3 install -r requirements.txt
