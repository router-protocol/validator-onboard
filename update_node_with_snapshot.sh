#!/bin/bash
# Title: Router Chain Installer
# Desc: This script will reset routerd and apply snapshot

clear
echo "---------------------------------"
echo "Router Chain Installer"
echo "---------------------------------"

SNAPSHOT_URL=$1

if [[ -z "$SNAPSHOT_URL" ]]; then
    echo "Snap shot url is not provided. Using default snapshot url"
    SNAPSHOT_URL="https://routerchain-testnet-snapshot.s3.ap-south-1.amazonaws.com/routerd_snapshot_20230622104858.tar.lz4"
fi

# Check if the system is Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "This script supports only Linux machines now."
    exit
fi

# Confirm user to reset routerd
printf "\nThis script will reset routerd and apply snapshot. Do you want to continue? (yes/no)\n"
read answer
if [[ "${answer,,}" != "yes" ]]; then
    echo "Exiting."
    exit 1
fi

# confirm user whether .routerd is backed up
printf "\nHave you backed up your %s/.routerd folder? (yes/no)\n" "$HOME"
read -r answer
if [[ "${answer,,}" != "yes" ]]; then
    echo "Please backup your .routerd folder and run this script again."
    exit 1
fi

# check if lz4 is installed
if ! command -v lz4 &>/dev/null; then
    echo "lz4 is not installed. Do you want to install it? (yes/no)"
    read answer
    if [[ "${answer,,}" == "yes" ]]; then
        sudo apt-get update
        sudo apt-get install -y lz4
    else
        echo "lz4 is required to run this script. Exiting."
        exit 1
    fi
fi

# check if cosmovisor.service is running, stop it if it is running
if [[ $(systemctl is-active cosmovisor.service) == "active" ]]; then
    echo "Stopping cosmovisor.service..."
    sudo systemctl stop cosmovisor.service
fi

echo "Reset routerd..."
routerd tendermint unsafe-reset-all --home "$HOME"/.routerd

# download snapshot
echo "Downloading snapshot..."
mkdir -p "$HOME"/router_chain_snapshots
cd "$HOME"/router_chain_snapshots || exit
SNAPSHOT_FILE_NAME=$(echo "$SNAPSHOT_URL" | awk -F'/' '{print $NF}')
wget -O "$SNAPSHOT_FILE_NAME" "$SNAPSHOT_URL"

# apply snapshot
echo "Applying snapshot..."
lz4 -c -d "$SNAPSHOT_FILE_NAME" | tar --checkpoint=.8192 --checkpoint-action=dot -x -C "$HOME"/.routerd

# start cosmovisor.service
echo "Starting cosmovisor.service..."
sudo systemctl start cosmovisor.service

# delete snapshot
echo "Deleting snapshot..."
rm -rf "$SNAPSHOT_FILE_NAME"
