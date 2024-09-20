# Router Useful Commands

## Key Management

### Add a New Key
```bash
routerd keys add wallet
```

### Recover an Existing Key
```bash
routerd keys add wallet --recover
```

### List All Keys
```bash
routerd keys list
```

### Delete a Key
```bash
routerd keys delete wallet
```

### Export a Key to a File
```bash
routerd keys export wallet
```

### Import a Key from a File
```bash
routerd keys import wallet wallet.backup
```

### Query Wallet Balance
```bash
routerd q bank balances $(routerd keys show wallet -a)
```

## Validator Management

### Create a New Validator
```bash
routerd tx staking create-validator \
  --amount 1000000000000000000route \
  --pubkey $(routerd tendermint show-validator) \
  --moniker "YOUR_MONIKER_NAME" \
  --identity "YOUR_KEYBASE_ID" \
  --details "YOUR_DETAILS" \
  --website "YOUR_WEBSITE_URL" \
  --chain-id router_9600-1 \
  --commission-rate 0.05 \
  --commission-max-rate 0.20 \
  --commission-max-change-rate 0.05 \
  --min-self-delegation 1 \
  --from wallet \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Edit an Existing Validator
```bash
routerd tx staking edit-validator \
  --new-moniker "YOUR_MONIKER_NAME" \
  --identity "YOUR_KEYBASE_ID" \
  --details "YOUR_DETAILS" \
  --website "YOUR_WEBSITE_URL" \
  --chain-id router_9600-1 \
  --commission-rate 0.05 \
  --from wallet \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Unjail a Validator
```bash
routerd tx slashing unjail \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Query Jail Reason
```bash
routerd query slashing signing-info $(routerd tendermint show-validator)
```

### List All Active Validators
```bash
routerd q staking validators -oj --limit=3000 | jq '.validators[] | select(.status=="BOND_STATUS_BONDED")' | jq -r '(.tokens|tonumber/pow(10; 18)|floor|tostring) + " \t " + .description.moniker' | sort -gr | nl
```

### List All Inactive Validators
```bash
routerd q staking validators -oj --limit=3000 | jq '.validators[] | select(.status=="BOND_STATUS_UNBONDED")' | jq -r '(.tokens|tonumber/pow(10; 18)|floor|tostring) + " \t " + .description.moniker' | sort -gr | nl
```

### View Validator Details
```bash
routerd q staking validator $(routerd keys show wallet --bech val -a)
```

## Token Management

### Withdraw All Rewards from Validators
```bash
routerd tx distribution withdraw-all-rewards \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Withdraw Commission and Rewards from Your Validator
```bash
routerd tx distribution withdraw-rewards $(routerd keys show wallet --bech val -a) \
  --commission \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Delegate Tokens to Yourself
```bash
routerd tx staking delegate $(routerd keys show wallet --bech val -a) 1000000000000000000route \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Delegate Tokens to Another Validator
```bash
routerd tx staking delegate <TO_VALOPER_ADDRESS> 1000000000000000000route \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Redelegate Tokens to Another Validator
```bash
routerd tx staking redelegate $(routerd keys show wallet --bech val -a) <TO_VALOPER_ADDRESS> 1000000000000000000route \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Unbond Tokens from Your Validator
```bash
routerd tx staking unbond $(routerd keys show wallet --bech val -a) 1000000000000000000route \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Send Tokens to Another Wallet
```bash
routerd tx bank send wallet <TO_WALLET_ADDRESS> 1000000000000000000route \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

## Governance

### List All Proposals
```bash
routerd query gov proposals
```

### View Proposal by ID
```bash
routerd query gov proposal 1
```

### Vote 'Yes' on a Proposal
```bash
routerd tx gov vote 1 yes \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Vote 'No' on a Proposal
```bash
routerd tx gov vote 1 no \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Vote 'Abstain' on a Proposal
```bash
routerd tx gov vote 1 abstain \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

### Vote 'NoWithVeto' on a Proposal
```bash
routerd tx gov vote 1 NoWithVeto \
  --from wallet \
  --chain-id router_9600-1 \
  --gas "200000" \
  --fees 5000route \
  -y
```

## Other Useful Commands

### Update Ports
```bash
CUSTOM_PORT=110
sed -i -e "s%^proxy_app = \"tcp://127.0.0.1:26658\"%proxy_app = \"tcp://127.0.0.1:${CUSTOM_PORT}58\"%; s%^laddr = \"tcp://127.0.0.1:26657\"%laddr = \"tcp://127.0.0.1:${CUSTOM_PORT}57\"%; s%^pprof_laddr = \"localhost:6060\"%pprof_laddr = \"localhost:${CUSTOM_PORT}60\"%; s%^laddr = \"tcp://0.0.0.0:26656\"%laddr = \"tcp://0.0.0.0:${CUSTOM_PORT}56\"%; s%^prometheus_listen_addr = \":26660\"%prometheus_listen_addr = \":${CUSTOM_PORT}66\"%" $HOME/.routerd/config/config.toml
sed -i -e "s%^address = \"tcp://0.0.0.0:1317\"%address = \"tcp://0.0.0.0:${CUSTOM_PORT}17\"%; s%^address = \":8080\"%address = \":${CUSTOM_PORT}80\"%; s%^address = \"0.0.0.0:9090\"%address = \"0.0.0.0:${CUSTOM_PORT}90\"%; s%^address = \"0.0.0.0:9091\"%address = \"0.0.0.0:${CUSTOM_PORT}91\"%" $HOME/.routerd/config/app.toml
```

### Update Indexer

#### Disable Indexer
```bash
sed -i -e 's|^indexer *=.*|indexer = "null"|' $HOME/.routerd/config/config.toml
```

#### Enable Indexer
```bash
sed -i -e 's|^indexer *=.*|indexer = "kv"|' $HOME/.routerd/config/config.toml
```

### Update Pruning
```bash
sed -i \
  -e 's|^pruning *=.*|pruning = "custom"|' \
  -e 's|^pruning-keep-recent *=.*|pruning-keep-recent = "100"|' \
  -e 's|^pruning-keep-every *=.*|pruning-keep-every = "0"|' \
  -e 's|^pruning-interval *=.*|pruning-interval = "19"|' \
  $HOME/.routerd/config/app.toml
```

### Get Validator Info
```bash
routerd status 2>&1 | jq .ValidatorInfo
```

### Get Sync Info
```bash
routerd status 2>&1 | jq .SyncInfo
```

### Get Node Peer
```bash
echo $(routerd tendermint show-node-id)'@'$(curl -s ifconfig.me)':'$(cat $HOME/.routerd/config/config.toml | sed -n '/^laddr = /s|^.*:||p')
```
