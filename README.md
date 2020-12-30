# cadCAD Golem

## Work in progress - due date 5 January 2021 - [https://gitcoin.co/issue/golemfactory/hackathons/3/100024408]

This package is a wrapper for cadCAD to dispatch the simulation workload to multiple Golem nodes.

[cadCAD](https://github.com/cadCAD-org/cadCAD) is a Python package that assists in the processes of designing, testing and validating complex systems through simulation, with support for Monte Carlo methods, A/B testing and parameter sweeping.

## Getting Started

### Initialise/Create environment and working directory
If you are already using cadCAD, activate the virtual environment that you use for cadCAD. This might look something like:
```bash
source ~/.venv/cadcad
```

If you do not yet have a working directory or virtual environment, creat both and activate. Something like so:
```bash
mkdir -p ~/projects/cadcad
cd ~/projects/cadcad
python3 -m venv .venv
source .venv/bin/activate
```

Now you have an isolated environment where you can install your python packages without fear of bloating the rest of your system.

### Install cadcadgolem
Requires [>= Python 3.8](https://www.python.org/downloads/)

#### Install Using [pip](https://pypi.org/project/cadCAD/)
```bash
$ pip3 install cadcadgolem
```

### Install *yagna daemon*

The Yagna daemon is what you will use to interface with the Golem network. It runs in the background, waiting for API calls from your applications, in our case, from *cadcadgolem*.

To install yagna, you can use their helper script:
```
curl -sSf https://join.golem.network/as-requestor | bash -
```

For manual installation instructions, see: [https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development]

To check it is installed corretly, run:
```
yagna --version
```

### Prepare *yagna daemon*
To run the yagna daemon, follow the following sequence. This sequence will need to be followed everytime you restart *yagna*.

#### Start the daemon
This will initialise the daemon
```
yagna service run
```

#### Generate the app key
```
yagna app-key create requestor
```

This should produce a 32-character-long hexadecimal app key that you need to note down as it will be needed in your code to run the requestor agent.

#### Get some coinage
Golem currently has a faucit where you can get free tokens to pay for the processing that you will perform on the network.
```
yagna payment init -r
```

#### Check that the fund transfer was successfull.
```
yagna payment status
```

#### Add your app-key to your code
When using cadcadgolem, a dictionary is passed that contains the parameters for your interaction with the network. One of them is yor app-eky, which allows you to speak to the *yagna* daemon that you started earlier. Place your app-key into your dictionary (see dictionary below).

## Using cadcad Golem

To use cadcad Golem, you need to do two things:
1. Define the golem_conf dictionary:
    ```
    golem_conf = {
            'NODES': 3, # Number of nodes to utilise from the Golem Network
            'BUDGET': 10.0, # Maximum amount of crypto you are prepared to spend
            'SUBNET': "community.3", # choose your subnet, currently this is the test network
            'YAGNA_APPKEY': '<YOUR-YAGNA_APPKEY-GOES HERE>', # get this from `yagna app-key list`
            'TIMEOUT': 120 # In seconds
            }
    ```
    (Example)[https://github.com/rogervs/cadcad_models/blob/2e61a84d1f28b23a3e0e9ef01f3c1f4fd4c85b2d/simple_cadcad.py#L75-L81]
    
2. Wrap your cadcad `Executor` in the cadcad Golem `Ambassador`:
    ```
    Executor = Ambassador(Executor, golem_conf)
    ```
    (Example)[https://github.com/rogervs/cadcad_models/blob/2e61a84d1f28b23a3e0e9ef01f3c1f4fd4c85b2d/simple_cadcad.py#L83]

For a simple cadCAD implementation, see (simple_cadcad.py)[https://github.com/rogervs/cadcad_models/blob/master/simple_cadcad.py]

## Security Notice
The communication on the Golem network is currently not encrypted, so do not use this for any sensitive data.
