#!/bin/bash

# Title: Router chain health check script
# Usage: bash validate_health.sh <validator_operator_address>
# Usage (output in json): bash validate_health.sh <validator_operator_address> --output json
# get oprerator address using: routerd keys show my-validator-key --bech=val --keyring-backend file -a

VALIDATOR_ADDRESS=$1

if [[ "${VALIDATOR_ADDRESS}" != "routervaloper"* ]]; then
    echo -e "\nNot a valid operator address. Exiting"
    echo -e $"\nUsage:\n\u2022 bash validate_health.sh <validator_operator_address>"
    echo -e $"\u2022 (output in json): bash validate_health.sh <validator_operator_address> --output json"
    echo -e "\nValidator operator address can be obtained using: routerd keys show <VALIDATOR_KEY_NAME> --bech=val --keyring-backend file -a\n"
    exit 1
fi

ROUTERD_SERVICE_NAME="cosmovisor.service"
ORCHESTRATOR_SERVICE_NAME="orchestrator.service"
LCD_ENDPOINT="http://localhost:1317"
ORCHESTRATOR_ENDPOINT="http://localhost:8001"
TM_RPC_ENDPOINT="http://localhost:26657"
PUBLIC_TM_RPC_ENDPOINT="https://tm.rpc.testnet.routerchain.dev/status"
PUBLIC_LCD_ENDPOINT="https://lcd.testnet.routerchain.dev"
MAX_CPU_PERCENT=80.0

declare -a SUCCESS_MSGS=()
declare -a ERROR_MSGS=()
declare -a ERROR_ENUMS=()
declare -a SUCCESS_ENUMS=()

# Check if --output json is passed as an argument
output_json=false
if [[ "$2" == "--output" && "$3" == "json" ]]; then
    output_json=true
fi

if ! $output_json; then
    clear
fi

echo() {
    if ! $output_json; then
        builtin echo "$@"
    fi
}

error_index=0
add_error_msg() {
    ERROR_MSGS[error_index]="$1"
    ERROR_ENUMS[error_index]="$2"
    error_index=$((error_index + 1))
}

success_index=0
add_success_msg() {
    SUCCESS_MSGS[success_index]="$1"
    SUCCESS_ENUMS[success_index]="$2"
    success_index=$((success_index + 1))
}

function check_usage() {
    local usage=$1
    local max_limit=$2
    local enum_key=$3
    local usage_type=$4

    if (($(echo "$usage > $max_limit" | bc -l))); then
        msg="${usage_type} usage is greater than ${max_limit}%"
        echo "${msg}"
        add_error_msg "$msg" "$enum_key"
    else
        msg="${usage_type} usage is at ${usage}%; remains under ${max_limit}% threshold"
        echo "${msg}"
        add_success_msg "$msg" "$enum_key"
    fi
}

echo "==============================="
echo "  Router Chain Health Check"
echo "==============================="
# Check if the system is Linux
if [[ "$(uname)" != "Linux" ]]; then
    if [[ "${output_json}" != true ]]; then
        echo "This script supports only Linux machines now"
    fi
    exit
fi

echo -e "\nChecking if the ${ROUTERD_SERVICE_NAME} service is active"
echo "---------------------------------"
ENUM_KEY="COSMOVISOR_SERVICE"
if ! systemctl is-active --quiet "${ROUTERD_SERVICE_NAME}"; then
    msg="The ${ROUTERD_SERVICE_NAME} (routerd) is NOT active"
    echo "${msg}"
    add_error_msg "$msg" "$ENUM_KEY"
else
    msg="The ${ROUTERD_SERVICE_NAME} (routerd) is active"
    echo "${msg}"
    add_success_msg "$msg" "$ENUM_KEY"
fi

ENUM_KEY="TMRPC_LOCAL"
echo -e "\nChecking if localhost tmRPC is accessible"
is_service_running=false
# check if able to access http://localhost:26657/status
if ! curl -s ${TM_RPC_ENDPOINT}/status >/dev/null; then
    msg="Unable to access ${TM_RPC_ENDPOINT}/status"
    echo "${msg}"
    add_error_msg "$msg" "$ENUM_KEY"
else
    is_service_running=true
    msg="Able to access ${TM_RPC_ENDPOINT}/status"
    echo "${msg}"
    add_success_msg "$msg" "$ENUM_KEY"
fi

ENUM_KEY="BLOCK_HEIGHT_UPDATE"
echo -e "\nChecking if the blocks are increasing (after waiting for 10 seconds)"
echo "---------------------------------"

if [[ "${is_service_running}" == true ]]; then
    CURRENT_BLOCK=$(curl -s ${TM_RPC_ENDPOINT}/status | jq -r '.result.sync_info.latest_block_height')

    sleep 10

    CURRENT_BLOCK_AFTER_WAIT=$(curl -s ${TM_RPC_ENDPOINT}/status | jq -r '.result.sync_info.latest_block_height')

    if [[ "${CURRENT_BLOCK}" == "${CURRENT_BLOCK_AFTER_WAIT}" ]]; then
        msg="Blocks are NOT increasing after waiting for 10 seconds. ${ROUTERD_SERVICE_NAME} is NOT syncing"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="Blocks are increasing. ${ROUTERD_SERVICE_NAME} is syncing"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi

    ENUM_KEY="BLOCK_HEIGHT_SYNC"
    LATEST_BLOCK=$(curl -s ${PUBLIC_TM_RPC_ENDPOINT} | jq -r '.result.sync_info.latest_block_height')

    if ((CURRENT_BLOCK < LATEST_BLOCK - 10 || CURRENT_BLOCK > LATEST_BLOCK + 10)); then
        msg="routerd service is NOT in sync with the public RPC"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="routerd service is in sync with the public RPC"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi

    ENUM_KEY="ORCHESTRATOR_SERVICE"
    echo -e "\nChecking if the ${ORCHESTRATOR_SERVICE_NAME} is syncing"
    echo "---------------------------------"
    if ! systemctl is-active --quiet "${ORCHESTRATOR_SERVICE_NAME}"; then
        msg="${ORCHESTRATOR_SERVICE_NAME} is NOT active"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="${ORCHESTRATOR_SERVICE_NAME} is active"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi

    ENUM_KEY="ORCHESTRATOR_HEALTH"
    echo -e "\nChecking orchestrator health"
    echo "---------------------------------"
    if ! curl -s ${ORCHESTRATOR_ENDPOINT}/health >/dev/null; then
        msg="Orchestrator process is NOT healthy"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="Orchestrator process is healthy"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi
fi

ENUM_KEY="BOND_STATUS"
echo -e "\nChecking if the validator is bonded"
echo "---------------------------------"
if [[ -n "${VALIDATOR_ADDRESS}" ]]; then
    echo "Provided validator address: ${VALIDATOR_ADDRESS}"
    VALIDATOR_BOND_STATUS=$(curl -s ${PUBLIC_LCD_ENDPOINT}/cosmos/staking/v1beta1/validators/"${VALIDATOR_ADDRESS}" | jq -r '.validator.status')
    echo "Validator status: ${VALIDATOR_BOND_STATUS}"
    if [[ "${VALIDATOR_BOND_STATUS}" == "BOND_STATUS_UNBONDED" ]]; then
        msg="The validator is NOT bonded"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="Validator status ${VALIDATOR_BOND_STATUS}. The validator is bonded"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi
fi

ENUM_KEY="JAIL_STATUS"
echo -e "\nChecking if the validator is jailed"
echo "---------------------------------"
if [[ -n "${VALIDATOR_ADDRESS}" ]]; then
    echo "Provided validator address: ${VALIDATOR_ADDRESS}"
    VALIDATOR_JAILED_STATUS=$(curl -s ${LCD_ENDPOINT}/staking/validators/"${VALIDATOR_ADDRESS}" | jq -r '.validator.jailed')

    if [[ "${VALIDATOR_JAILED_STATUS}" == "true" ]]; then
        msg="The validator is jailed"
        echo "${msg}"
        add_error_msg "$msg" "$ENUM_KEY"
    else
        msg="The validator is not jailed"
        echo "${msg}"
        add_success_msg "$msg" "$ENUM_KEY"
    fi
fi

# check if the system CPU, Memory, Disk usage is normal
if dpkg -s sysstat &>/dev/null; then
    echo "sysstat is available"
else
    echo "sysstat is not installed. Attempting to install"

    # Install sysstat. This command requires root permissions.
    if sudo apt-get install -y sysstat; then
        echo "sysstat installed successfully"
    else
        echo "Unable to install sysstat. Skipping system health check"
    fi
fi

if dpkg -s sysstat &>/dev/null; then
    echo -e "\nSystem CPU, Memory, Disk usage"

    cpu_usage=$(mpstat | awk '$12 ~ /[0-9.]+/ { print 100 - $12 }')
    mem_usage=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
    disk_usage=$(df -h | awk '$NF=="/"{printf "%s", $5}' | tr -d %)

    echo "---------------------------------"
    echo "CPU usage: ${cpu_usage}%"
    echo "Memory usage: ${mem_usage}%"
    echo "Disk usage: ${disk_usage}%"

    echo "Validating system health.."
    check_usage "$cpu_usage" $MAX_CPU_PERCENT "CPU_USAGE" "CPU"
    check_usage "$mem_usage" 80 "MEMORY_USAGE" "Memory"
    check_usage "$disk_usage" 80 "DISK_USAGE" "Disk"
fi

#######################################
########## Print the result ###########
#######################################

echo -e "\nResult"
echo "---------------------------------"

for msg in "${SUCCESS_MSGS[@]}"; do
    echo -e "\xE2\x9C\x94 ${msg}"
done

# print all the error messages, add a cross mark and new line at the end of each message
for msg in "${ERROR_MSGS[@]}"; do
    echo -e "\xE2\x9D\x8C ${msg}"
done

total_errors=${#ERROR_MSGS[@]}
total_success=${#SUCCESS_MSGS[@]}
total_checks=$((total_errors + total_success))

# Summary
if [[ "${output_json}" != true ]]; then
    echo -e "\nSummary"
    echo "---------------------------------"
    echo -e "Total checks: ${total_checks}"
    echo -e "Success: ${total_success}"
    echo -e "Error: ${total_errors}"
fi

function generate_json() {
    local enums=("${!1}")
    local msgs=("${!2}")
    local status=$3
    local json='['

    for ((i = 0; i < ${#enums[@]}; i++)); do
        if [ $i -ne 0 ]; then
            json+=", "
        fi
        json+=$(printf '{"type": "%s", "status": "%s", "msg": "%s"}' "${enums[$i]}" "$status" "${msgs[$i]}")
    done

    json+=']'
    echo "$json"
}

# Check if --output json is passed as an argument
if [[ "${output_json}" == true ]]; then
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    output_json=false

    SUCCESS_MSGS_JSON=$(generate_json SUCCESS_ENUMS[@] SUCCESS_MSGS[@] "HEALTHY")
    ERROR_MSGS_JSON=$(generate_json ERROR_ENUMS[@] ERROR_MSGS[@] "UNHEALTHY")

    if ! dpkg -s jq &>/dev/null; then
        echo -e "{\"total_checks\": ${total_checks},\"success\": ${total_success},\"error\": ${total_errors},\"timestamp\": \"${timestamp}\",\"success_msgs\": ${SUCCESS_MSGS_JSON},\"error_msgs\": ${ERROR_MSGS_JSON}}"
        exit 1
    fi
    echo -e "{\"total_checks\": ${total_checks},\"success\": ${total_success},\"error\": ${total_errors},\"timestamp\": \"${timestamp}\",\"success_msgs\": ${SUCCESS_MSGS_JSON},\"error_msgs\": ${ERROR_MSGS_JSON}}" | jq
fi
