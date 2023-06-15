# router-chain-validator-onboard

## Setup validator

1. Use this shell command to start validator onboard process. Following command will setup node by installing all required dependencies, create systemd service and start node.

```shell
curl -L https://bit.ly/3IdpohH > r.sh && bash r.sh
```

2. Follow this documentation to stake and configure orchestrator: <https://docs.routerprotocol.com/validators/running-a-validator/on-testnet/run-a-node>

## Validator health check

1. Use this shell command to check validator health. Following command will check node status, orchestrator status and validator status.

```shell
curl -L https://bit.ly/440dal3  > vh.sh && bash vh.sh <validator operator address>
```

Note: You can find validator operator address using

```shell
routerd keys show <validator_key> -a --keyring-backend file --bech=val
```

there is a optional `--output json` flag to get output in json format
