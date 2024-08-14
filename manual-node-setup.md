# Routerd Installation Guide for Mainnet Node (Manual)

## Pre-requisites
- Install Go v1.21.0: https://golang.org/doc/install
```bash
wget -q -O - https://git.io/vQhTU | bash -s -- --version 1.21.0
```

- Install jq: https://stedolan.github.io/jq/download/

## Copy Dependencies
```bash
wget https://github.com/CosmWasm/wasmvm/releases/download/v1.5.2/libwasmvm.x86_64.so
cp libwasmvm.x86_64.so /lib
cp libwasmvm.x86_64.so /lib64
```

## Download Binary: 
```bash
wget https://raw.githubusercontent.com/router-protocol/router-chain-binary-release/v2.1.6/linux/routerd.tar.gz
tar -xvf routerd.tar.gz -C .
chmod +x /usr/bin/routerd
cp routerd /usr/bin

# Check if routerd is installed
routerd version
```

## Init node and download genesis

```bash
export MONIKER="node-moniker"
routerd init $MONIKER  --chain-id router_9600-1
wget -O - https://sentry.tm.rpc.routerprotocol.com/genesis | jq '.result.genesis' > $HOME/.routerd/config/genesis.json
```

## Add peers
Add the following peers to your config.toml file in the .routerd/config directory

```bash
persistent_peers = "ebc272824924ea1a27ea3183dd0b9ba713494f83@router-mainnet-seed.autostake.com:27336,13a59edcee8ede7afa62ae054f266b44701cedc0@213.246.45.16:3656,10fec659763badc3ec55b845c2e6c17a70e77fd5@51.195.104.64:15656,49e4a20d999fe27868a67fc72bc6bf0e1424a610@188.214.133.133:26656,28459bddd2049d31cf642792e6bb87676edaee1e@65.109.61.125:23756,3f2556a0e390fa6f049e85fc0b27064f9ebdb9d7@57.129.28.26:26656,e90a88795977f7cc24982d5684f0f5a4581cd672@185.8.104.157:26656,fbb30fa866f318e9e1c48188711526fc69f66d18@188.214.133.174:26656"
```

## Download snapshot
```bash
cd $HOME/.routerd
wget https://ss.router.nodestake.org/2024-08-14_router_8781099.tar.lz4
lz4 -d 2024-08-14_router_8781099.tar.lz4 | tar -xvf -
```

## Add Cosmovisor
```bash
go install cosmossdk.io/tools/cosmovisor/cmd/cosmovisor@v1.5.0
export DAEMON_NAME=routerd
export DAEMON_RESTART_AFTER_UPGRADE=true
export DAEMON_HOME=$HOME/.routerd
cosmovisor init $(which routerd)
cosmovisor add-upgrade 2.1.1-nitro-to-2.1.6 $(which routerd) --upgrade-height 7673000
```

## Start the node

```bash
export routerd_home = $HOME/.routerd
cosmovisor run start --log_level "error" --json-rpc.api eth,txpool,personal,net,debug,web3,miner --api.enable start --trace "true" --home $routerd_home
```
Note: 
1. You can change the log_level to "info" or "debug" to get more logs.
2. Create a systemd service to run the node in the background.

```bash
[Unit]
Description=Cosmovisor Daemon for Routerd
After=network-online.target

[Service]
User=current-user # Change this to the user you want to run the node as
Environment="DAEMON_NAME=routerd"
Environment="DAEMON_HOME=/home/current-user/.routerd" # Change this to the home directory of the user
Environment="DAEMON_RESTART_AFTER_UPGRADE=true"
Environment="DAEMON_ALLOW_DOWNLOAD_BINARIES=false"
Environment="DAEMON_LOG_BUFFER_SIZE=512"
Environment="UNSAFE_SKIP_BACKUP=true"
ExecStart=cosmovisor run start \
          --log_level "info" \
          --json-rpc.api eth,txpool,personal,net,debug,web3,miner \
          --api.enable start \
          --trace "true" \
          --home $DAEMON_HOME
Restart=always
RestartSec=3
LimitNOFILE=infinity
LimitNPROC=infinity

[Install]
WantedBy=multi-user.target
```
