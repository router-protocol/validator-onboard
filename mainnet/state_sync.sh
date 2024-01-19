#!/bin/bash
# Title: Router Chain Installer

echo "---------------------------------"
echo "Router Chain snapshot installer"
echo "---------------------------------"

SNAP_RPC=$1
if [[ -z "$SNAP_RPC" ]]; then
  echo "Usage: $0 <SNAP_RPC>"
  exit 1
fi
LATEST_HEIGHT=$(curl -s "$SNAP_RPC/block" | jq -r .result.block.header.height)
BLOCK_HEIGHT=$((LATEST_HEIGHT - 1000))

TRUST_HASH=$(curl -s "$SNAP_RPC/block?height=$BLOCK_HEIGHT" | jq -r .result.block_id.hash)

echo
echo "Latest Height: $LATEST_HEIGHT"
echo "Block Height to Trust: $BLOCK_HEIGHT"
echo "Trust Hash: $TRUST_HASH"

CONFIG_FILE="$HOME/.routerd/config/config.toml"

sed -i.bak -E \
  -e "s|^(enable[[:space:]]+=[[:space:]]+).*|\1true|" \
  -e "s|^(rpc_servers[[:space:]]+=[[:space:]]+).*|\1\"$SNAP_RPC,$SNAP_RPC\"|" \
  -e "s|^(trust_height[[:space:]]+=[[:space:]]+).*|\1$BLOCK_HEIGHT|" \
  -e "s|^(trust_hash[[:space:]]+=[[:space:]]+).*|\1\"$TRUST_HASH\"|" \
  -e "s|^(seeds[[:space:]]+=[[:space:]]+).*|\1\"\"|" "$CONFIG_FILE"

echo
echo "Updated Configuration:"
grep 'enable\|rpc_servers\|trust_height\|trust_hash\|seeds' "$CONFIG_FILE"