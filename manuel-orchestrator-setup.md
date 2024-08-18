# Router Orchestrator Installation Guide

## 1. Update and Install Dependencies

Start by updating your system and installing the required dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git wget gzip -y
```

## 2. Install Orchestrator

Download and extract the Orchestrator binary:

```bash
cd $HOME
wget -O router-orchestrator.tar.gz https://github.com/router-protocol/router-orchestrator-binary-release/raw/main/linux/router-orchestrator.tar.gz
tar -C $HOME/go/bin -xzf router-orchestrator.tar.gz
rm router-orchestrator.tar.gz
```

## 3. Set Orchestrator Service Files

Create and configure the systemd service file for the Orchestrator:

```bash
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
```

## 4. Launch Orchestrator

Reload the systemd daemon, enable, and start the Orchestrator service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable router-orchestrator
sudo systemctl start router-orchestrator
```

## 5. Monitor Orchestrator Logs

To monitor the real-time logs of the Router Orchestrator service, use the following command:

```bash
journalctl -fu router-orchestrator -o cat
```
