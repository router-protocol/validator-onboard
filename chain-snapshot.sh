#!/bin/bash
# Title: Router chain snapshot script
# usage: bash chain-snapshot.sh </path/to/.routerd> </snapshot/output/path>

echo "START SNAPSHOT SCRIPT: [$(date)] $0 $1 $2"

ROUTERD_HOME=$1
SNAPSHOT_OUTPUT_PATH=$2
UPLOAD_TO_S3=$3

service_name="cosmovisor.service"

if [[ -z "${ROUTERD_HOME}" ]]; then
    echo "routerd home is not provided. Exiting."
    exit 1
fi

if [[ -z "${SNAPSHOT_OUTPUT_PATH}" ]]; then
    echo "snapshot output path is not provided. Exiting."
    exit 1
fi

# validate ROUTERD_HOME directory exists
if [[ ! -d "${ROUTERD_HOME}" ]]; then
    echo "routerd home directory does not exist. Exiting."
    exit 1
fi

# validate SNAPSHOT_OUTPUT_PATH directory exists
if [[ ! -d "${SNAPSHOT_OUTPUT_PATH}" ]]; then
    echo "snapshot output path directory does not exist. Exiting."
    exit 1
fi

# Check if the system is Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "This script supports only Linux machines now."
    exit
fi

# check if lz4 is installed
if ! command -v lz4 &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y lz4
fi

if ! command -v lz4 &>/dev/null; then
    echo "lz4 is required to run this script. Exiting."
    exit 1
fi

# stop routerd service

echo "Stopping ${service_name} service"
sudo systemctl stop ${service_name}

cd "${ROUTERD_HOME}" || exit 1

snapshot_file_name="routerd-snapshot-$(date +%Y-%m-%d).tar.lz4"
# append date to the snapshot file name
tar cvf - data/ wasm/ | lz4 >"${SNAPSHOT_OUTPUT_PATH}/${snapshot_file_name}"

echo "Snapshot created successfully at ${SNAPSHOT_OUTPUT_PATH}/${snapshot_file_name}"

# start routerd service
sudo systemctl start ${service_name}
echo "Started ${service_name} service"

if [[ -z "${UPLOAD_TO_S3}" ]]; then
    echo "UPLOAD_TO_S3 is not provided. Exiting."
    exit 1
fi

# check if aws cli is installed
if ! command -v aws &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y awscli
fi

if ! command -v aws &>/dev/null; then
    echo "aws cli is required to run this script. Exiting."
    exit 1
fi

bucket_name=""
bucket_path=""

# validate bucket_name and bucket_path
if [[ -z "${bucket_name}" ]]; then
    echo "bucket_name is not provided. Exiting."
    exit 1
fi
if [[ -z "${bucket_path}" ]]; then
    echo "bucket_path is not provided. Exiting."
    exit 1
fi 

# upload file to S3
aws s3 cp "${SNAPSHOT_OUTPUT_PATH}/${snapshot_file_name}" "s3://${bucket_name}/${bucket_path}/${snapshot_file_name}"
echo "Snapshot uploaded successfully to s3://${bucket_name}/${bucket_path}/${snapshot_file_name}"