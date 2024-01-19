#!/bin/bash
# Title: Router Validator Installation

# Clear the screen
clear

# Display the header
echo "---------------------------------"
echo " Router Chain Installer"
echo "---------------------------------"


GIT_URL="https://bit.ly/47Jd6aX"
VALIDATOR_ONBOARD_URL="validator_onboard.py"

cleanup() {
    echo "clean up"
    rm -- "$0"
    rm -- "${VALIDATOR_ONBOARD_URL}"
}

trap cleanup EXIT

# Check if the system is Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "This script supports only Linux machines now."
    exit
fi

# Check if wget is installed
if ! command -v wget &> /dev/null
then
    echo "wget could not be found"
    exit 1
fi

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Do you want to install it? (yes/no)"
    read answer
    if [[ "${answer,,}" == "yes" ]]; then
        sudo apt-get update
        sudo apt-get install -y python3
    else
        echo "Python3 is required to run this script. Exiting."
        exit 1
    fi
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Do you want to install it? (yes/no)"
    read answer
    if [[ "${answer,,}" == "yes" ]]; then
        sudo apt-get update
        sudo apt-get install -y python3-pip
    else
        echo "pip is required to run this script. Exiting."
        exit 1
    fi
fi

# Check if requests library is installed
if ! python3 -c "import requests" &> /dev/null; then
    echo "The requests library is not installed. Do you want to install it? (yes/no)"
    read answer
    if [[ "${answer,,}" == "yes" ]]; then
        pip3 install --user requests
    else
        echo "The requests library is required to run this script. Exiting."
        exit 1
    fi
fi

# check if python3 traceback library is installed
if ! python3 -c "import traceback" &> /dev/null; then
    echo "The traceback library is not installed. This is required to trace if any errors occur during the script execution."
    echo "Do you want to install it? (yes/no)"
    read answer
    if [[ "${answer,,}" == "yes" ]]; then
        pip3 install --user traceback
    else
        echo "Traceback not installed. Continuing without it."
    fi
fi

if command -v curl &> /dev/null; then
    curl -L -o "${VALIDATOR_ONBOARD_URL}" "${GIT_URL}"
elif command -v wget &> /dev/null; then
    wget -O "${VALIDATOR_ONBOARD_URL}" "${GIT_URL}"
else
    echo "curl or wget is required to download the Python script. Please install one of them and try again."
    exit 1
fi

# EXPECTED_CHECKSUM="f2a8c8855bdd1be6773851eacf518025c3b6cb29dce936a8aea07e0bac85d2ac"
# checksum=$(sha256sum "${VALIDATOR_ONBOARD_URL}" | awk '{print $1}')

# if [ "$checksum" = "$EXPECTED_CHECKSUM" ]; then
#     python3 "${VALIDATOR_ONBOARD_URL}"
# else
#     echo "Checksum validation failed. The downloaded file may be corrupted."
#     exit
# fi
python3 "${VALIDATOR_ONBOARD_URL}"