#! /bin/bash

cd /golem/work

source /opt/venv/bin/activate

python3 /golem/work/golem-diplomat.py &> /golem/output/sh.log || true
