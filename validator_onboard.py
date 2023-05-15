from enum import Enum
import os
import subprocess
import platform
import json
import requests
import argparse
import sys
import shutil
import random
from subprocess import check_call

# self-destruct file after first call
# os.remove(sys.argv[0])


class NetworkVersion(str, Enum):
    TESTNET = "v1.0.0-rc1"
version = NetworkVersion.TESTNET
snapshot_url="https://snapshots.routerprotocol.com/router-testnet-snapshot-2021-09-30-00-00-00.tar.gz"
class NetworkType(str, Enum):
    MAINNET = "1"
    TESTNET = "2"


SEED_PEERS="06952dd421e75835e8871de3f60507812156ea03@13.127.165.58:26656"
GENESIS_JSON="https://tm.rpc.testnet.routerchain.dev/genesis"
ROUTERD_FILE = "routerd.tar"
ORCHESTRATORD_FILE = "router-orchestrator"
ROUTER_REPO = "https://raw.githubusercontent.com/router-protocol/router-chain-releases/main/linux"
ORCHESTRATOR_REPO = "https://raw.githubusercontent.com/router-protocol/router-chain-releases/main/linux"

ORCHESTRATOR_TEMPLATE="""
{
    "chains": [
        {
            "chainId": "<CHAIN_ID>",
            "chainType": "<CHAIN_TYPE>",
            "chainName": "<CHAIN_NAME>",
            "chainRpc": "<CHAIN_RPC>",
            "blocksToSearch": 1000,
            "blockTime": "10s"
        }
    ],
    "globalConfig": {
        "networkType": "<NETWORK_TYPE>",
        "dbPath": "processedblock.db",
        "ethPrivateKey": "<ETH_PRIVATE_KEY>",
        "cosmosPrivateKey": "<COSMOS_PRIVATE_KEY>",
        "batchSize": 100,
        "batchWaitTime": 20
    }
}"""

ENABLE_SNAPSHOT = False
HOME_DIR = os.path.expanduser("~")

SYSTEM_RAM_REQUIRED = 16

os_name = platform.system()
machine = platform.machine()

def clear_screen(showTitle=True):
    print("clear screen")
    subprocess.run(["clear"], shell=True)
    if showTitle:
        print('''Router Chain Installer \n''')

def colorprint(message):
    print(message)

class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        return ', '.join(action.option_strings)

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

def fmt(prog): return CustomHelpFormatter(prog, max_help_position=30)

parser = argparse.ArgumentParser(
    description="Router Installer", formatter_class=fmt)


routerd_service_file_content = '''[Unit]
Description=routerd
After=network.target

[Service]
User=ubuntu
Group=ubuntu
Type=simple
ExecStart=/usr/bin/routerd start --json-rpc.api eth,txpool,personal,net,debug,web3,miner --api.enable start --trace "true"

[Install]
WantedBy=multi-user.target
'''

orchestrator_service_file_content = '''[Unit]
Description=orchestrator
After=network.target

[Service]
User=ubuntu
Group=ubuntu
Type=simple

WorkingDirectory=/home/ubuntu/.router-orchestrator
ExecStart=/usr/bin/router-orchestrator start --reset --config /home/ubuntu/.router-orchestrator/config.json

[Install]
WantedBy=multi-user.target
'''

parser._optionals.title = 'Optional Arguments'
if not len(sys.argv) > 1:
    parser.set_defaults(mainnetDefault=False, testnetDefault=False, swapOn=None, installHome=None, nodeName=None, ports=None, nodeType=None, network=None, pruning=None, cosmovisorService=None,
                        dataSyncTestnet=None, snapshotTypeTestnet=None, dataSync=None, snapshotType=None, snapshotLocation=None, replayDbBackend=None, extraSwap=None, startReplay=None)

args = parser.parse_args()
if args.testnetDefault == True:
    args.network = 'router_9000-1'
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

pruning_settings_choices = [
    {
        "name": "Default",
        "description": "The last 362880 states are kept, pruning at 10 block intervals"
    },
    {
        "name": "Nothing",
        "description": "All historic states will be saved, nothing will be deleted (i.e. archiving node)"
    },
    {
        "name": "Everything",
        "description": "Allow pruning options to be manually specified through 'pruning-keep-recent', and 'pruning-interval'"
    },
    {
        "name": "Custom",
        "description": "Store the most recent 10,000 states and prune at random prime block interval"
    }
]

snapshot_options = [
    {
        "name": "Download a snapshot (recommended)",
        "description": "Download a pre-built snapshot of the blockchain for faster synchronization."
    },
    {
        "name": "Sync from genesis",
        "description": "Synchronize the blockchain from the beginning (slow but secure)."
    },
    {
        "name": "Exit now, I only wanted to install the daemon",
        "description": "Exit the installer without synchronizing the blockchain."
    }
]

def init_node_name():
    global nodeName
    nodeName = NetworkType.TESTNET
    print("testnet running: "+nodeName, " home: "+routerd_home)
    clear_screen()
    remove_directory(routerd_home)
    
    remove_directory(os.path.join(HOME_DIR, ".routerd"))
    print(bcolors.OKGREEN + "Initializing Router Node " + nodeName + bcolors.ENDC)
    setup_testnet()

def remove_directory(path):
    # check if directory already exists? if yes prompt to delete
    if os.path.isdir(path):
        response = input(f"The directory {path} exists. Do you want to delete it? (y/n): ")
        if response.lower() in ["y", "yes"]:
            subprocess.run(["rm -r " + path], stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, shell=True, env=my_env)
            print(f"Directory {path} has been deleted.")
        else:
            print("Directory not deleted.")


def setup_testnet():
    print(bcolors.OKGREEN + "Initializing Router Node " + nodeName + bcolors.ENDC)
    clear_screen()
    setup_router_node()
    download_replace_genesis()
    # customPortSelection()
    

def setup_router_node():
    clear_config_files()
    subprocess.run(["routerd init " + nodeName + " --chain-id=router_9000-1 -o --home " + routerd_home],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)

def clear_config_files():
    for file in ["config/config.toml", "config/app.toml", "config/addrbook.json"]:
        remove_file(os.path.join(routerd_home, file))

def remove_file(file_path):
    subprocess.run(["rm " + file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)

def download_replace_genesis():
    colorprint("Downloading and Replacing Genesis...")
    download_genesis()
    replace_genesis()
    unsafe_reset()
    find_replace_seeds()
    pruning_settings()
    # start_routerd_service()

def start_routerd_service():
    # ask user confirmation to add service file and start
    # if yes, add service file and start
    # else, exit
    print(bcolors.OKGREEN + """Do you want to setup routerd as a service?:
1) Yes (recommended)
2) No (you will have to manually start routerd)
""" + bcolors.ENDC)
    choice = input("Enter your choice: ")
    if choice == "1":
        print(bcolors.OKGREEN + "Setting up routerd as a service..." + bcolors.ENDC)
        setup_service()
        start_service()
    elif choice == "2":
        print(bcolors.OKGREEN + "Skipping routerd service setup..." + bcolors.ENDC)
    else:
        print(bcolors.FAIL + "Invalid choice. Please try again." + bcolors.ENDC)
        start_routerd_service()

def setup_service():
    # stop if already running
    subprocess.run(["sudo systemctl stop routerd.service"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)
    with open("routerd.service", "w") as service_file:
        service_file.write(routerd_service_file_content)

    # shutil.copy("routerd.service", "/etc/systemd/system/")
    subprocess.run(
        ["sudo mv routerd.service /lib/systemd/system/routerd.service"], shell=True, env=my_env)
    subprocess.run(["sudo systemctl daemon-reload"], shell=True, env=my_env)



def start_service():

    subprocess.run(["systemctl daemon-reload"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)
    subprocess.run(["systemctl enable routerd.service"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)
    subprocess.run(["systemctl start routerd.service"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)
    subprocess.run(["systemctl status routerd.service"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)

def unsafe_reset():
    print(bcolors.OKGREEN + "Resetting routerd..." + bcolors.ENDC)
    subprocess.run(["routerd unsafe-reset-all --home " + routerd_home],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)

def download_genesis():
    subprocess.run(["wget -O " + os.path.join(routerd_home, "config/genesis.json") + " wget "+GENESIS_JSON],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)

def replace_genesis():
    print("replacing genesis...")
    with open(os.path.join(routerd_home, "config/genesis.json"), "r") as json_file:
        data = json.load(json_file)

    result_genesis = data.get("result", {}).get("genesis")
    # data["genesis"] = result_genesis

    # print("replace genesis... with: ", data["genesis"])
    with open(os.path.join(routerd_home, "config/genesis.json"), "w") as json_file:
        json.dump(result_genesis, json_file, indent=4)

def find_replace_seeds():
    colorprint("Finding and Replacing Seeds...")
    replace_seeds(SEED_PEERS)

def replace_seeds(peers):
    config_toml = os.path.join(routerd_home, "config/config.toml")
    subprocess.run(["sed -i -E 's/persistent_peers = \"\"/persistent_peers = \"" + peers + "\"/g' " + config_toml], shell=True)
    subprocess.run(["sed -i -E 's/seeds = \"\"/seeds = \"" + peers + "\"/g' " + config_toml], shell=True)
    clear_screen()

def customPortSelection():
    print("Not implemented yet")
    # Your custom port selection function implementation


def pruning_settings():

    print(f"{bcolors.OKGREEN}Please choose your desired pruning settings:")
    for i, setting in enumerate(pruning_settings_choices, start=1):
        print(f"{i}) {setting['name']}: ({setting['description']})")
    # 1 - default
    # 2 - nothing
    # 3 - everything
    # 4 - custom
    pruneAns = input(bcolors.OKGREEN + 'Enter Choice: ' + bcolors.ENDC)

    if pruneAns == "1":
        clear_screen()
        dataSyncSelectionTest()
    elif pruneAns == "2":
        clear_screen()
        subprocess.run(["sed -i -E 's/pruning = \"default\"/pruning = \"nothing\"/g' " +
                       routerd_home+"/config/app.toml"], shell=True)
        dataSyncSelectionTest()
    elif pruneAns == "3":
        clear_screen()
        subprocess.run(["sed -i -E 's/pruning = \"default\"/pruning = \"everything\"/g' " +
                       routerd_home+"/config/app.toml"], shell=True)
        dataSyncSelectionTest()
    elif pruneAns == "4":
        primeNum = random.choice([x for x in range(11, 97) if not [
                                 t for t in range(2, x) if not x % t]])
        clear_screen()
        subprocess.run(["sed -i -E 's/pruning = \"default\"/pruning = \"custom\"/g' " +
                       routerd_home+"/config/app.toml"], shell=True)
        subprocess.run(["sed -i -E 's/pruning-keep-recent = \"0\"/pruning-keep-recent = \"10000\"/g' " +
                       routerd_home+"/config/app.toml"], shell=True)
        subprocess.run(["sed -i -E 's/pruning-interval = \"0\"/pruning-interval = \"" +
                       str(primeNum)+"\"/g' "+routerd_home+"/config/app.toml"], shell=True)
        dataSyncSelectionTest()
    else:
        clear_screen()
        pruning_settings()

def dataSyncSelectionTest():
    print(f"{bcolors.OKGREEN}Please choose from the following options:")
    for i, option in enumerate(snapshot_options, start=1):
        print(f"{i}) {option['name']}: ({option['description']})")
        print(f"{bcolors.ENDC}")
    dataTypeAns = input(bcolors.OKGREEN + 'Enter Choice: ' + bcolors.ENDC)
    # 1 - Download snapshot
    # 2 - Sync from genesis
    # 3 - exit
    if dataTypeAns == "1":
        clear_screen()
        testNetType()
    elif dataTypeAns == "2":
        clear_screen()
        cosmovisorInit()
    elif dataTypeAns == "3":
        clear_screen()
        partComplete()
    else:
        clear_screen()
        dataSyncSelectionTest()

def testNetType():
    if ENABLE_SNAPSHOT == False:
        print(bcolors.OKGREEN + "Snapshot is disabled. Please choose another option" + bcolors.ENDC)
        dataSyncSelectionTest()

    # continue with snapshot
    global fileName
    global location
    
    fileName = "routertestnet-4-pruned"
    snapshotInstall()

def partComplete():
    print(bcolors.OKGREEN +
          "Congratulations! You have successfully completed setting up the Router daemon!")
    print(bcolors.OKGREEN +
          "The routerd service is NOT running in the background, and your data directory is empty")
    print(bcolors.OKGREEN + "If you intend to use routerd without syncing, you must include the '--node' flag after cli commands with the address of a public RPC node" + bcolors.ENDC)
    quit()

def snapshotInstall():
    colorprint("Downloading Decompression Packages...")
    if os_name == "Linux":
        subprocess.run(["sudo apt-get install wget liblz4-tool aria2 -y"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    colorprint("Downloading Snapshot from " + snapshot_url + " ...")
    os.chdir(os.path.expanduser(routerd_home))
    subprocess.run(["wget -O - "+snapshot_url +
                   " | lz4 -d | tar -xvf -"], shell=True, env=my_env)
    clear_screen()
    if os_name == "Linux":
        cosmovisorInit()
    else:
        complete()

def complete():
    print(bcolors.OKGREEN +
          "Congratulations! You have successfully completed setting up an Routerd full node!")
    print(bcolors.OKGREEN + "The routerd service is NOT running in the background")
    print(bcolors.OKGREEN +
          "You can start routerd with the following command: 'routerd start'" + bcolors.ENDC)
    quit()

def install_location():
    global routerd_home
    print(bcolors.OKGREEN + """Do you want to install routerd in the default location?:
1) Yes, use default location (recommended)
2) No, specify custom location
""" + bcolors.ENDC)
    if args.installHome:
        location_choice = '2'
    else:
        location_choice = input(
            bcolors.OKGREEN + 'Enter Choice for location: ' + bcolors.ENDC)
    print("location choice: " + location_choice)
    if location_choice == "1":
        clear_screen()
        routerd_home = subprocess.run(
            ["echo $HOME/.routerd"], capture_output=True, shell=True, text=True).stdout.strip()
    elif location_choice == "2":
        clear_screen()
        locationChoice = input(bcolors.OKGREEN + 'Enter Choice for 2: ' + bcolors.ENDC)
        if locationChoice.strip() == "":
            locationChoice = "$HOME/.routerd"
        routerd_home = subprocess.run(
            [f"echo {locationChoice}"], capture_output=True, shell=True, text=True).stdout.strip()
    else:
        clear_screen()
        install_location()
    init_node_name()

def install_location_handler():
    # not implemented yet
    print("Not implemented yet")
    # Your custom install location handler function implementation

def download_and_copy_libs():
    if os.path.exists("routerd-libs"):
        shutil.rmtree("routerd-libs")

    check_call(["git", "clone", "https://github.com/router-protocol/routerd-libs"])

    for src_file in os.listdir("routerd-libs"):
        src_path = os.path.join("routerd-libs", src_file)
        if os.path.isfile(src_path):
            subprocess.run(["sudo cp "+src_path +
                " /lib"], shell=True, env=my_env)
            subprocess.run(["sudo cp "+src_path +
                " /lib64"], shell=True, env=my_env)

def cosmovisorInit():
    print(bcolors.OKGREEN + "Initializing cosmovisor..." + bcolors.ENDC)
    clear_screen()
    os.chdir(os.path.expanduser(HOME))

    colorprint("Setting Up Cosmovisor...")
    subprocess.run(["go install github.com/cosmos/cosmos-sdk/cosmovisor/cmd/cosmovisor@v1.0.0"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)
    subprocess.run(["mkdir -p "+routerd_home+"/cosmovisor"],
                       shell=True, env=my_env)
    subprocess.run(
        ["mkdir -p "+routerd_home+"/cosmovisor/genesis"], shell=True, env=my_env)
    subprocess.run(
        ["mkdir -p "+routerd_home+"/cosmovisor/genesis/bin"], shell=True, env=my_env)
    subprocess.run(
        ["mkdir -p "+routerd_home+"/cosmovisor/upgrades"], shell=True, env=my_env)
    subprocess.run(
        ["mkdir -p "+routerd_home+"/cosmovisor/upgrades/v1/bin"], shell=True, env=my_env)

    subprocess.run(["cp /usr/bin/routerd "+routerd_home+"/cosmovisor/upgrades/v1/bin"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, env=my_env)
    subprocess.run(["cp /usr/bin/routerd "+routerd_home +
                    "/cosmovisor/genesis/bin"], shell=True, env=my_env)
    cosmovisorService()
    clear_screen()
    completeCosmovisor()

def cosmovisorService():
    colorprint("Creating Cosmovisor Service")
    os.chdir(os.path.expanduser(HOME))
    subprocess.run(["echo '# Setup Cosmovisor' >> "+HOME +
                   "/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export DAEMON_NAME=routerd' >> " +
                   HOME+"/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export DAEMON_HOME="+routerd_home +
                   "' >> "+HOME+"/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export DAEMON_ALLOW_DOWNLOAD_BINARIES=false' >> " +
                   HOME+"/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export DAEMON_LOG_BUFFER_SIZE=512' >> " +
                   HOME+"/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export DAEMON_RESTART_AFTER_UPGRADE=true' >> " +
                   HOME+"/.profile"], shell=True, env=my_env)
    subprocess.run(["echo 'export UNSAFE_SKIP_BACKUP=true' >> " +
                   HOME+"/.profile"], shell=True, env=my_env)
    #print HOME
    subprocess.run(["echo $HOME - "+HOME], shell=True, env=my_env)
    subprocess.run(["""echo '[Unit]
Description=Cosmovisor daemon
After=network-online.target
[Service]
Environment=\"DAEMON_NAME=routerd\"
Environment=\"DAEMON_HOME=""" + routerd_home+"""\"
Environment=\"DAEMON_RESTART_AFTER_UPGRADE=true\"
Environment=\"DAEMON_ALLOW_DOWNLOAD_BINARIES=false\"
Environment=\"DAEMON_LOG_BUFFER_SIZE=512\"
Environment=\"UNSAFE_SKIP_BACKUP=true\"
User =""" + USER+"""
ExecStart="""+HOME+"""/go/bin/cosmovisor start --json-rpc.api eth,txpool,personal,net,debug,web3,miner --api.enable start --trace "true" --home """+routerd_home+"""
Restart=always
RestartSec=3
LimitNOFILE=infinity
LimitNPROC=infinity
[Install]
WantedBy=multi-user.target
' >cosmovisor.service
    """], shell=True, env=my_env)
    subprocess.run(
        ["sudo mv cosmovisor.service /lib/systemd/system/cosmovisor.service"], shell=True, env=my_env)
    subprocess.run(["sudo systemctl daemon-reload"], shell=True, env=my_env)

    clear_screen()

def completeCosmovisor():
    print(bcolors.OKGREEN + "Cosmovisor Service Created" + bcolors.ENDC)
    print(bcolors.OKGREEN + "Start service by running 'sudo systemctl start cosmovisor.service'" + bcolors.ENDC)
    print(bcolors.OKGREEN + "To see the status of cosmovisor, run the following command: 'systemctl status cosmovisor'")
    colorprint(
        "To see the live logs from cosmovisor, run the following command: 'journalctl -u cosmovisor -f'")
    if install_option == 2:
        quit()

def get_go_executable_path():
    result = subprocess.run(['which', 'go'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print('GO Installation complete. Please restart your terminal or run `source ~/.bashrc` to apply changes.')
        # exit if not installed
        exit(1)
        # return None

    go_executable_path = result.stdout.strip()
    return go_executable_path

def get_gopath(go_executable_path):
    result = subprocess.run([go_executable_path, 'env', 'GOPATH'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error getting GOPATH.")
        return None

    gopath = result.stdout.strip()
    return gopath

def init_setup():
    global my_env
    global GOPATH
    clear_screen()
    print(bcolors.OKGREEN + "Installing Dependencies" + bcolors.ENDC)
    if os_name == "Linux":
        colorprint("(1/4) Updating Packages...")
        subprocess.run(["sudo apt-get update"],
        stdout=subprocess.DEVNULL, shell=True)
        subprocess.run(["sudo DEBIAN_FRONTEND=noninteractive apt-get -y upgrade"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        colorprint("(2/4) Installing make and GCC...")
        subprocess.run(["sudo apt install git build-essential ufw curl jq snapd --yes"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

        colorprint("(3/4) Installing Go...")
        subprocess.run(["wget -q -O - https://git.io/vQhTU | bash -s -- --remove"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        subprocess.run(["wget -q -O - https://git.io/vQhTU | bash -s -- --version 1.19"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        # go_executable_path = get_go_executable_path()
        # if go_executable_path:
        #     GOPATH = get_gopath(go_executable_path)
        os.chdir(os.path.expanduser(HOME_DIR))
        print(bcolors.OKGREEN +
            "(4/4) Installing Router {v} Binary...".format(v=version) + bcolors.ENDC)

        response = requests.get(f"{ROUTER_REPO}/routerd.tar")
        with open(os.path.join(HOME_DIR, ROUTERD_FILE), "wb") as f:
            f.write(response.content)
        subprocess.run(["tar -xvf routerd.tar -C ."], shell=True)
        subprocess.run(["sudo cp routerd /usr/bin"], shell=True)
        clear_screen()
        colorprint("Router {v} Installed Successfully!".format(v=version))
        colorprint("Installing dependencies...")
        my_env = os.environ.copy()
        my_env["PATH"] = "/"+HOME+"/go/bin:/"+HOME + \
            "/go/bin:/"+HOME+"/.go/bin:" + my_env["PATH"]
        download_and_copy_libs()
        colorprint("Type 'routerd' to start routerd")
    else:
        print("Unknown OS")


def setup():
    global HOME
    global USER
    global GOPATH
    HOME = subprocess.run(
            ["echo $HOME"], capture_output=True, shell=True, text=True).stdout.strip()
    USER = subprocess.run(
            ["echo $USER"], capture_output=True, shell=True, text=True).stdout.strip()
    GOPATH = HOME+"/go"
    if os_name == "Linux":
        print(bcolors.OKGREEN + "System Detected: Linux" + bcolors.ENDC)
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gib = mem_bytes/(1024.**3)
        print(bcolors.OKGREEN + "RAM Detected: " +
        str(round(mem_gib))+"GB" + bcolors.ENDC)            
        if mem_gib < SYSTEM_RAM_REQUIRED:
            print(bcolors.FAIL + "Not enough RAM to run routerd" + bcolors.ENDC)
            print(bcolors.OKCYAN + "Do you want to continue? (y/n)" + bcolors.ENDC)
            choice = input().lower()
            if choice == "n":
                exit(1)
            elif choice == "y":
                pass
        init_setup()
        install_location()
    elif os_name == "Darwin":
        print("Mac OS is not supported yet \n")
        exit(1)
    elif os_name == "Windows":
        print("Windows is not supported yet \n")
        exit(1)
    else:
        print("Unknown OS")
        exit(1)

def setup_orchestrator():
    global HOME
    global USER
    global GOPATH
    HOME = subprocess.run(
            ["echo $HOME"], capture_output=True, shell=True, text=True).stdout.strip()
    USER = subprocess.run(
            ["echo $USER"], capture_output=True, shell=True, text=True).stdout.strip()
    GOPATH = HOME+"/go"
    if os_name == "Linux":
        install_orchestrator()
        configure_orchestrator()
    elif os_name == "Darwin":
        print("Mac")
    elif os_name == "Windows":
        print("Windows")
    else:
        print("Unknown OS")

def install_orchestrator():
    print(bcolors.OKGREEN + "Installing Orchestrator..." + bcolors.ENDC)
    response = requests.get(f"{ORCHESTRATOR_REPO}/{ORCHESTRATORD_FILE}")
    with open(os.path.join(HOME_DIR, ORCHESTRATORD_FILE), "wb") as f:
        f.write(response.content)
    subprocess.run(["sudo cp router-orchestrator /usr/bin"], shell=True)
    subprocess.run(["sudo chmod +x /usr/bin/router-orchestrator"], shell=True)
    download_and_copy_libs()
    setup_orchestrator_service()

def setup_orchestrator_service():
    # stop if already running
    print(bcolors.OKGREEN + "Setting up Orchestrator Service..." + bcolors.ENDC)
    subprocess.run(["sudo systemctl stop orchestrator.service"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, shell=True, env=my_env)
    with open("orchestrator.service", "w") as service_file:
        service_file.write(orchestrator_service_file_content)

    subprocess.run(
        ["sudo mv orchestrator.service /lib/systemd/system/orchestrator.service"], shell=True, env=my_env)
    subprocess.run(["sudo systemctl daemon-reload"], shell=True, env=my_env)

def configure_orchestrator():
    print(bcolors.OKGREEN + "Configuring Orchestrators..." + bcolors.ENDC)
    dir_name = ".router-orchestrator"
    dir_path = os.path.join(HOME_DIR, dir_name)
    print(f"Current directory: {os.getcwd()}")
    print(f"Checking if directory '{dir_name}' exists")
    if not os.path.exists(dir_path):
        print(f"Creating directory '{dir_name}'")
        os.mkdir(dir_path)
    else:
        print(f"Directory '{dir_name}' exists")
    os.chdir(os.path.expanduser(dir_path))
    config_data = json.loads(ORCHESTRATOR_TEMPLATE)
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent='', separators=(',', ':'))
    print("\nOrchestrator config created successfully. Please edit config to add chains and private keys")
    print("Run 'sudo systemctl start orchestrator.service' to start orchestrator")
    print("Run 'journalctl -fu orchestrator.service -u -f' to see logs")

def start():
    global my_env
    global version
    global install_option
    my_env = os.environ.copy()
    clear_screen(False)
    print(bcolors.OKGREEN + """
    
██████╗░░█████╗░██╗░░░██╗████████╗███████╗██████╗░  ░█████╗░██╗░░██╗░█████╗░██╗███╗░░██╗
██╔══██╗██╔══██╗██║░░░██║╚══██╔══╝██╔════╝██╔══██╗  ██╔══██╗██║░░██║██╔══██╗██║████╗░██║
██████╔╝██║░░██║██║░░░██║░░░██║░░░█████╗░░██████╔╝  ██║░░╚═╝███████║███████║██║██╔██╗██║
██╔══██╗██║░░██║██║░░░██║░░░██║░░░██╔══╝░░██╔══██╗  ██║░░██╗██╔══██║██╔══██║██║██║╚████║
██║░░██║╚█████╔╝╚██████╔╝░░░██║░░░███████╗██║░░██║  ╚█████╔╝██║░░██║██║░░██║██║██║░╚███║
╚═╝░░╚═╝░╚════╝░░╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝  ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝

    ROUTER CHAIN INSTALLER
    Testnet version: {t}
        """.format(
        t=NetworkVersion.TESTNET.value) + bcolors.ENDC)
    # select to install router or orchestrator
    print("Select an option:")
    print("1. Install Validator (routerd) & Orchestrator")
    print("2. Install Validator (routerd)")
    print("3. Install Orchestrator")
    option = input("Enter option: ")
    
    if option == "1":
        install_option=1
        print(bcolors.OKBLUE + "Installing Router and Orchestrator" + bcolors.ENDC)
        setup()
        setup_orchestrator()
        configure_orchestrator()
        print(bcolors.OKGREEN + "Run validator (routerd) using" + bcolors.ENDC)
        install_option=2
        completeCosmovisor()
    elif option == "2":
        install_option=2
        print("Installing Router...")
        setup()
    elif option == "3":
        install_option=3
        setup_orchestrator()

    else:
        print("Invalid option")
        exit(1)

if __name__ == '__main__':
    start()