#!/bin/bash

# Installation function
install_orchestrator() {
    echo "Updating the system and installing dependencies..."
    sudo apt update && sudo apt upgrade -y
    sudo apt install git wget gzip -y

    echo "Downloading and installing the Orchestrator..."
    cd $HOME
    wget -qO- https://github.com/router-protocol/router-orchestrator-binary-release/raw/main/linux/router-orchestrator.tar.gz | tar -C $HOME/go/bin -xz

    # Ask user for input
    read -p "Enter the IP address of your server: " server_ip
    read -p "Enter the EVM address: " evm_address
    read -p "Enter the Cosmos address: " cosmos_address
    read -p "Enter the Ethereum private key: " eth_private_key
    read -p "Enter the Cosmos private key: " cosmos_private_key

    echo "Creating config.json file..."
    mkdir -p $HOME/.router-orchestrator
    cat <<EOF > $HOME/.router-orchestrator/config.json
{
   "chains": [
   ],
   "globalConfig": {
      "logLevel": "debug",
      "networkType": "mainnet",
      "networkId": "router_9600-1",
      "dbPath": "orchestrator.db",
      "batchSize": 25,
      "batchWaitTime": 4,
      "_routerChainTmRpc": "http://$server_ip:26657",
      "_routerChainGRpc": "tcp://$server_ip:9090",
      "evmAddress": "$evm_address",
      "cosmosAddress": "$cosmos_address",
      "ethPrivateKey": "$eth_private_key",
      "cosmosPrivateKey": "$cosmos_private_key"
   }
}
EOF

    echo "Creating Orchestrator service file..."
    sudo tee /etc/systemd/system/router-orchestrator.service > /dev/null <<EOF
[Unit]
Description="Router Orchestrator Service"
After=network-online.target

[Service]
User=$USER
Type=simple
ExecStart=$(which router-orchestrator) start --config $HOME/.router-orchestrator/config.json
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

    echo "Starting the service..."
    sudo systemctl daemon-reload
    sudo systemctl enable router-orchestrator
    sudo systemctl start router-orchestrator

    echo "Installation complete."
}

# Uninstallation function
uninstall_orchestrator() {
    echo "Stopping the Orchestrator service..."
    sudo systemctl stop router-orchestrator

    echo "Removing the Orchestrator service..."
    sudo systemctl disable router-orchestrator
    sudo rm /etc/systemd/system/router-orchestrator.service
    sudo systemctl daemon-reload

    echo "Deleting Orchestrator files..."
    rm -rf $HOME/.router-orchestrator
    rm -f $HOME/go/bin/router-orchestrator

    echo "Uninstallation complete."
}

# Provide user with options
echo "Router Orchestrator Installation Script"
echo "1. Start Installation"
echo "2. Uninstall"
read -p "Please choose an option (1/2): " choice

# Execute the appropriate function based on the user's choice
case $choice in
    1)
        install_orchestrator
        ;;
    2)
        uninstall_orchestrator
        ;;
    *)
        echo "Invalid choice! Please select 1 or 2."
        ;;
esac
