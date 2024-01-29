#!/bin/bash

get_distro_id_lsb_release() {
    lsb_release -i | cut -f 2
}

get_distro_id_os_release() {
    grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"'
}

if systemctl is-active --quiet cosmovisor.service; then
    echo "cosmovisor.service is running, please stop it and try again"
    exit 1
fi


distro_id=""
current_version="v1.2.4-to-v1.2.5"

# Check if lsb_release is available
if command -v lsb_release &> /dev/null; then
    distro_id=$(get_distro_id_lsb_release)
elif [ -f /etc/os-release ]; then
    distro_id=$(get_distro_id_os_release)
fi
distro_id=$(echo "$distro_id" | tr '[:upper:]' '[:lower:]')
if [ "$distro_id" != "ubuntu" ] && [ "$distro_id" != "debian" ]; then
    echo "Unsupported distro: $distro_id"
    exit 1
fi

dir_path=$HOME/update_routerd_29_jan
mkdir "$dir_path"
cd "$dir_path" || exit

routerd_url="https://raw.githubusercontent.com/router-protocol/router-chain-releases/main/linux/"
if [ "$distro_id" == "ubuntu" ]; then
    routerd_url="$routerd_url/routerd.tar"
elif [ "$distro_id" == "debian" ]; then
    routerd_url="$routerd_url/debian/routerd.tar"
else
    echo "Unsupported distro"
    exit 1
fi

wget "$routerd_url" -O routerd.tar
if [ -f routerd.tar ]; then
    echo "routerd.tar exists"
else
    echo "routerd.tar does not exist"
    exit 1
fi

tar -xvf routerd.tar
if [ -f routerd ]; then
    echo "routerd untarred"
else
    echo "routerd does not exist"
    exit 1
fi

routerd_chain_path=$HOME/.routerd/cosmovisor
if [ -d "$routerd_chain_path" ]; then
    echo "routerd_chain_path exists"
else
    echo "routerd_chain_path does not exist"
    exit 1
fi

routerd_binary_path=$(which routerd)
if [ -f "$routerd_binary_path" ]; then
    echo "routerd_binary_path exists"
    cp ./routerd "$routerd_binary_path"
fi
cp ./routerd "$routerd_chain_path/current/bin/routerd"
cp ./routerd "$routerd_chain_path/upgrades/$current_version/bin/routerd"

echo "Completed update, please restart cosmovisor.service"