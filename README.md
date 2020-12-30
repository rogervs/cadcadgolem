# cadCAD Golem

## Work in progress - due date 5 January 2021

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

### Installing
Requires [>= Python 3.8](https://www.python.org/downloads/)

**Option A: Install Using [pip](https://pypi.org/project/cadCAD/)** 
```bash
$ pip3 install cadcadgolem
```

**Option B:** Build From Source
```
$ pip3 install -r requirements.txt
$ python3 setup.py sdist bdist_wheel
$ pip3 install dist/*.whl
```
