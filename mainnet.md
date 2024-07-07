# Mainnet Setup

## Create config.json

Create config.json file using the following command:

```shell
nano config.json
```

and paste the following content in the config.json file:

```json
{
    "snapshot_url": "",
    "seed_peers": "",
    "genesis": "",
    "genesis_checksum": "",
    "snap_rpc_url": ""
}
```

## Setup validator

```shell
curl -L https://bit.ly/48BNjm4 > rv.sh && bash rv.sh config.json
```

### Setup using validator onboarding script

1. Select option 1 to install both node and orchestrator
   ![binary selection](img/image.png)
2. Or select option 2 or 3 to install only node or orchestrator respectively
   ![node or orchestrator](img/image-1.png)
3. State sync using one of the following options.
   1. Snapshot
   2. Fast sync
   3. Full node
   ![state sync](img/image-2.png)

   **Note:** Prefer to sync using snapshot (option 1) as it is reliable.
4. Start node

   start:   `sudo systemctl restart cosmovisor.service`

   check logs: `journalctl -u cosmovisor -f`
5. Start orchestrator

   start: `sudo systemctl restart orchestrator.service`

   check logs: `journalctl -u orchestrator -f`


### Setup validator account

1. Create validator account

   ```bash
   export VALIDATOR_KEY_NAME="my-validator-name"
   routerd keys add $VALIDATOR_KEY_NAME
   ```

2. Copy routerd address

   ```bash
   routerd keys show $VALIDATOR_KEY_NAME
   export VALIDATOR_ADDRESS=<routerd-address>
   source ~/.bashrc
   ```

3. Fund routerd address with some $ROUTE tokens and check balance

   ```bash
   routerd q bank balances $VALIDATOR_ADDRESS
   ```

4. Create validator: Initialize new validator with self delegation of $ROUTE tokens.

   ```bash
      export VALIDATOR_MONIKER="my-validator-moniker"

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

5. Verify validator status

   ```bash
   routerd q staking validator $VALIDATOR_ADDRESS
   ```

### Setup Orchestrator account

1. Create orchestrator account

   ```bash
   export ORCHESTRATOR_KEY_NAME="my-orchestrator-name"
   routerd keys add $ORCHESTRATOR_KEY_NAME
   ```

   get Orchestrator address

   ```bash
   routerd keys show $ORCHESTRATOR_KEY_NAME
   export ORCHESTRATOR_ADDRESS=<routerd-address>
   ```

2. Get funds to orchestrator account, check balance after getting funds

   ```bash
   routerd q bank balances $ORCHESTRATOR_ADDRESS
   ```

3. Map orchestrator address to validator address.

   `EVM-KEY-FOR-SIGNING-TXNS` is the public ethereum address. You can create one in Metamask, it doesnt need to have funds. We use it to sign transactions on EVM chains. Make sure to save the private key of this address somewhere safe.

   ```bash
   export EVM_ADDRESS_FOR_SIGNING_TXNS=<EVM-ADDRESS-FOR-SIGNING-TXNS>
   routerd tx attestation set-orchestrator-address $ORCHESTRATOR_ADDRESS $EVM_ADDRESS_FOR_SIGNING_TXNS --from $VALIDATOR_KEY_NAME \
   --chain-id router_9600-1 \
   --fees 1000000000000000route \
   ```

### Add config.json for Orchestrator
```bash
cd .router-orchestrator
nano config.json
```

   ```json
      {
         "chains": [
            {
               "chainId": "137",
               "chainType": "CHAIN_TYPE_EVM",
               "chainName": "Polygon",
               "chainRpc": "www.polygon-rpc.com",
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
            "routerChainTmRpc": "http://0.0.0.0:26657",
            "routerChainGRpc": "tcp://0.0.0.0:9090",
            "evmAddress": "",
            "cosmosAddress": "",
            "ethPrivateKey": "",
            "cosmosPrivateKey": ""
         }
      }
   ```

- `routerChainTmRpc` and `routerChainGRpc`, point it to your validator IP
- `cosmosAddress` is Router address of orchestrator // router5678abcd
- `cosmosPrivateKey` is private key for your orchestrator cosmos address (private key of above `cosmosAddress`)
- `evmAddress` is EVM address of orchestrator which created in above step in Metamask //0x1234abcd
- `ethPrivateKey` is private key for the the above `evmAddress` wallet you created
- `loglevel` currently kept it as "debug" can be set as "info" evmAddress is EVM address of orchestrator //0x1234abcd

### Start Validator and Orchestrator

1. Start validator

   ```bash
   sudo systemctl start cosmovisor.service
   sudo systemctl status cosmovisor.service

   # check logs
   journalctl -u cosmovisor -f
   ```

2. Start orchestrator

   ```bash
   sudo systemctl start orchestrator.service
   sudo systemctl status orchestrator.service

   # check logs
   journalctl -u orchestrator -f
   ```

### Check validator and orchestrator status

1. Check if node is syncing, make sure it is not stuck at some block height

   ```bash
   routerd status 2>&1 | jq .SyncInfo
   ```

2. Check if orchestrator health is ok

   ```bash
   curl localhost:8001/health
   ```
