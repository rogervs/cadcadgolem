# cadCAD Golem

## Work in progress - due date 5 January 2021 - (https://gitcoin.co/issue/golemfactory/hackathons/3/100024408)

This package is a wrapper for cadCAD to dispatch the simulation workload to multiple Golem nodes.

[cadCAD](https://github.com/cadCAD-org/cadCAD) is a Python package that assists in the processes of designing, testing and validating complex systems through simulation, with support for Monte Carlo methods, A/B testing and parameter sweeping.

[Golem](https://golem.network/) is a global, open source, decentralized supercomputer that anyone can access. It is made up of the combined power of users' machines, from PC's to entire data centers.

## Note

* Jupyter Notebook support added.

* The Golem network is still under development, and not all nodes behave perfectly. If your simulatino fails, try again a few times.

## Getting Started

### Initialise/Create environment and working directory
If you are already using cadCAD, activate the virtual environment that you use for cadCAD. This might look something like:
```bash
source ~/.venv/cadcad
```

If you do not yet have a working directory or virtual environment, creat both and activate. Something like so:
```bash
mkdir -p ~/projects/cadcad-exp
cd ~/projects/cadcad-exp
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

For manual installation instructions, see: (https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development)

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

#### Generate the app key (*This only has to done once after initial install of `yagna`*)
```
yagna app-key create requestor
```

This should produce a 32-character-long hexadecimal app key that you need to note down as it will be needed in your code to run the requestor agent.

#### Get some coinage
Golem currently has a faucet where you can get free tokens to pay for the processing that you will perform on the network.
```
yagna payment init -r
```

#### Check that the fund transfer was successfull.
```
yagna payment status
```

#### Add your app-key to your code
When using cadcadgolem, a dictionary is passed that contains the parameters for your interaction with the network. One of them is yor app-key, which allows you to speak to the *yagna* daemon that you started earlier. Place your app-key into your dictionary (see dictionary below).

## Using cadcad Golem

To use cadcad Golem, you need to do three things:

1. Import the cadcad Golem Ambassador:
```
from cadcadgolem.golem_embassy import Ambassador
```
2. Define the golem_conf dictionary:
    ```
    golem_conf = {
            'NODES': 3, # Number of nodes to utilise from the Golem Network. If you've got a big simulation to run, try pushing this up to 30. Remember you need at least twice as many simulation runs as you have nodes.
            'BUDGET': 10.0, # Maximum amount of crypto you are prepared to spend
            'SUBNET': "community.3", # choose your subnet, currently this is the test network
            'YAGNA_APPKEY': '<YOUR-YAGNA_APPKEY-GOES HERE>', # get this from `yagna app-key list`
            'TIMEOUT': 120 # In seconds - you will need to figure this out for your workload. Max currently is 25min, so 25 * 60 seconds
            }
    ```
    [Example](https://github.com/rogervs/cadcad_models/blob/2e61a84d1f28b23a3e0e9ef01f3c1f4fd4c85b2d/simple_cadcad.py#L75-L81)
    
3. Wrap your cadcad `Executor` in the cadcad Golem `Ambassador`:
    ```
    Executor = Ambassador(Executor, golem_conf)
    ```
    [Example](https://github.com/rogervs/cadcad_models/blob/2e61a84d1f28b23a3e0e9ef01f3c1f4fd4c85b2d/simple_cadcad.py#L83)

For a simple cadCAD implementation, see [simple_cadcad.py](https://github.com/rogervs/cadcad_models/blob/master/simple_cadcad.py)

## System initialisation after first install
1. `yagna service run`
2. `yagna payment init -r`
3. Run your cadCAD code!

## cadCAD Examples/Demos

You can find more cadCAD demos to play with here: https://github.com/cadCAD-org/demos
To modify them them to work with cadcadGolem, just add the golem_conf dictionary declaration as above, and then wrap the cadCAD `Executor` with the cadCADGolem `Ambassador` and you're done.

## Security Notice
The communication on the Golem network is currently not encrypted, so do not use this for any sensitive data.

## Caveats
You need at least twice as many simulation runs as you have nodes, else it the simulation will fail.
