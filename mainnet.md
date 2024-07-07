# Router Mainnet Installation Guide

## Step 1: Create the Configuration File

First, create a configuration file named `config.json`. Use the following command:

```shell
nano config.json
```

Paste the following content into the `config.json` file:

```json
{
    "snapshot_url": "",
    "seed_peers": "",
    "genesis": "",
    "genesis_checksum": "",
    "snap_rpc_url": ""
}
```

## Step 2: Setup the Validator

Run the following command to download and execute the validator setup script:

```shell
curl -L https://bit.ly/48BNjm4 > rv.sh && bash rv.sh config.json
```

### Validator Onboarding Script Options

1. **Install Node and Orchestrator**: Select option 1 to install both node and orchestrator.
   ![binary selection](img/image.png)

2. **Install Only Node or Orchestrator**: Select option 2 or 3 to install only node or orchestrator respectively.
   ![node or orchestrator](img/image-1.png)

3. **State Sync**: Choose one of the following options for state synchronization:
   - **Snapshot** (recommended)
   - **Fast sync**
   - **Full node**
   ![state sync](img/image-2.png)

   **Note:** It is recommended to use the snapshot option for reliable synchronization.

4. **Start the Node**:
   ```shell
   sudo systemctl restart cosmovisor.service
   ```
   Check logs:
   ```shell
   journalctl -u cosmovisor -f
   ```

5. **Start the Orchestrator**:
   ```shell
   sudo systemctl restart orchestrator.service
   ```
   Check logs:
   ```shell
   journalctl -u orchestrator -f
   ```

## Step 3: Setup Validator Account

1. **Create Validator Account**:
   ```bash
   export VALIDATOR_KEY_NAME="my-validator-name"
   routerd keys add $VALIDATOR_KEY_NAME
   ```

2. **Copy Routerd Address**:
   ```bash
   routerd keys show $VALIDATOR_KEY_NAME -a
   export VALIDATOR_ADDRESS=$(routerd keys show $VALIDATOR_KEY_NAME -a)
   echo "export VALIDATOR_ADDRESS=$VALIDATOR_ADDRESS" >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Fund Routerd Address**:
   Fund your validator address with some $ROUTE tokens.

   Check balance:
   ```bash
   routerd q bank balances $VALIDATOR_ADDRESS
   ```

4. **Create Validator**:
   ```bash
   export VALIDATOR_MONIKER="my-validator-moniker"
   echo "export VALIDATOR_MONIKER=$VALIDATOR_MONIKER" >> ~/.bashrc
   source ~/.bashrc

   routerd tx staking create-validator \
   --amount=1000000000000000000route \
   --pubkey=$(routerd tendermint show-validator) \
   --moniker=$VALIDATOR_MONIKER \
   --chain-id=router_9600-1 \
   --commission-rate="0.10" \
   --commission-max-rate="0.20" \
   --commission-max-change-rate="0.01" \
   --min-self-delegation="1000000" \
   --gas="auto" \
   --fees="100000000000000route" \
   --from=$VALIDATOR_KEY_NAME \
   --gas-adjustment=1.5 \
   --keyring-backend=file
   ```

5. **Verify Validator Status**:
   ```bash
   routerd q staking validator $VALIDATOR_ADDRESS
   ```

## Step 4: Setup Orchestrator Account

1. **Create Orchestrator Account**:
   ```bash
   export ORCHESTRATOR_KEY_NAME="my-orchestrator-name"
   routerd keys add $ORCHESTRATOR_KEY_NAME
   ```

   Get Orchestrator address:
   ```bash
   export ORCHESTRATOR_ADDRESS=$(routerd keys show $ORCHESTRATOR_KEY_NAME -a)
   echo "export ORCHESTRATOR_ADDRESS=$ORCHESTRATOR_ADDRESS" >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Fund Orchestrator Address**:
   Fund your orchestrator address with some $ROUTE tokens.

   Check balance:
   ```bash
   routerd q bank balances $ORCHESTRATOR_ADDRESS
   ```

3. **Map Orchestrator to Validator**:
   ```
   export EVM_ADDRESS_FOR_SIGNING_TXNS=<EVM-ADDRESS-FOR-SIGNING-TXNS>
   echo "export EVM_ADDRESS_FOR_SIGNING_TXNS=$EVM_ADDRESS_FOR_SIGNING_TXNS" >> ~/.bashrc
   source ~/.bashrc
    ```
    ```
    routerd tx attestation set-orchestrator-address <orchestrator-address> <eth-address-for-signing-txns> --from <validator-key-name> --chain-id router_9600-1 --fees         1000000000000000route -y
```

## Step 5: Add Configuration for Orchestrator

Create a configuration file for the orchestrator:

```
cd ~/.router-orchestrator
nano config.json
```

Paste the following content into the `config.json` file:

```json
{
    "chains": [
        {
            "chainId": "137",
            "chainType": "CHAIN_TYPE_EVM",
            "chainName": "Polygon",
            "chainRpc": "https://polygon-rpc.com",
            "blocksToSearch": 1000,
            "blockTime": "5s"
        }
    ],
    "globalConfig": {
        "logLevel": "debug",
        "networkType": "mainnet",
        "dbPath": "orchestrator.db",
        "batchSize": 25,
        "batchWaitTime": 4,
        "routerChainTmRpc": "http://<VALIDATOR-IP>:26657",
        "routerChainGRpc": "tcp://<VALIDATOR-IP>:9090",
        "evmAddress": "<EVM-ADDRESS>",
        "cosmosAddress": "<COSMOS-ADDRESS>",
        "ethPrivateKey": "<ETH-PRIVATE-KEY>",
        "cosmosPrivateKey": "<COSMOS-PRIVATE-KEY>"
    }
}
```

- `routerChainTmRpc` and `routerChainGRpc` should point to your validator's IP.
- `cosmosAddress` is the Router address of the orchestrator.
- `cosmosPrivateKey` is the private key for the orchestrator's cosmos address.
- `evmAddress` is the EVM address of the orchestrator (created in Metamask).
- `ethPrivateKey` is the private key for the EVM address created.

## Step 6: Start Validator and Orchestrator

1. **Start Validator**:
   ```bash
   sudo systemctl start cosmovisor.service
   sudo systemctl status cosmovisor.service

   # Check logs
   journalctl -u cosmovisor -f
   ```

2. **Start Orchestrator**:
   ```bash
   sudo systemctl start orchestrator.service
   sudo systemctl status orchestrator.service

   # Check logs
   journalctl -u orchestrator -f
   ```

## Step 7: Verify Status

1. **Check Node Syncing**:
   ```bash
   routerd status 2>&1 | jq .SyncInfo
   ```

2. **Check Orchestrator Health**:
   ```bash
   curl localhost:8001/health
   ```
