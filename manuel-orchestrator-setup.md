# Router Orchestrator Installation Guide

## 1. Update and Install Dependencies

Start by updating your system and installing the required dependencies:

```shell
sudo apt update && sudo apt upgrade -y
sudo apt install git wget gzip -y
```

## 2. Install Orchestrator

Download and extract the Orchestrator binary:

```shell
cd $HOME
wget -qO- https://github.com/router-protocol/router-orchestrator-binary-release/raw/main/linux/router-orchestrator.tar.gz | tar -C $HOME/go/bin -xz
```

## 3. Add `config.json` for Orchestrator

You need to create a `config.json` file for the Orchestrator with the following content:
```shell
nano $HOME/.router-orchestrator/config.json
```

```json
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
      "_routerChainTmRpc": "http://0.0.0.0:26657",
      "_routerChainGRpc": "tcp://0.0.0.0:9090",
      "evmAddress": "",
      "cosmosAddress": "",
      "ethPrivateKey": "",
      "cosmosPrivateKey": ""
   }
}
```

### Important Configuration Details:

- **`routerChainTmRpc` and `routerChainGRpc`**: Replace `0.0.0.0` with the IP address of your validator.
- **`cosmosAddress`**: This is the Router address of the Orchestrator (e.g., `router5678abcd`).
- **`cosmosPrivateKey`**: The private key corresponding to your Orchestrator’s Cosmos address (the one you provided for `cosmosAddress`).
- **`evmAddress`**: The EVM address of the Orchestrator, which was created in Metamask (e.g., `0x1234abcd`).
- **`ethPrivateKey`**: The private key for the above `evmAddress` wallet.

### Notes:

- The `logLevel` is currently set to `debug`. You can adjust this level based on your needs for logging verbosity.

## 4. Set Orchestrator Service Files

Create and configure the systemd service file for the Orchestrator:

```shell
sudo tee /etc/systemd/system/router-orchestrator.service > /dev/null <<EOF
[Unit]
Description="Router Orchestrator Service"
After=network-online.target

[Service]
User=$USER
Type=simple
ExecStart=$(which router-orchestrator) start --config $HOME/.router-orchestrator/config.json --reset
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF
```

## 5. Launch Orchestrator

Reload the systemd daemon, enable, and start the Orchestrator service:

```shell
sudo systemctl daemon-reload
sudo systemctl enable router-orchestrator
sudo systemctl start router-orchestrator
```

## 6. Monitor Orchestrator Logs

To monitor the real-time logs of the Router Orchestrator service, use the following command:

```shell
journalctl -fu router-orchestrator -o cat
```
