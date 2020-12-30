#!/usr/bin/python3.8

from cadCAD.configuration import Experiment
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Configuration
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor
import numpy as np
import dill
import pathlib
import re
import logging
from datetime import datetime
import platform

import sys

## Diretory setup
output_dir = pathlib.Path('/golem/output').resolve()
resource_dir = pathlib.Path('/golem/resource').resolve()

log_file = output_dir / 'output.log'
work_dir = pathlib.Path('/golem/work')

# Find the file to perform this job
pickle_files = resource_dir.glob('*.pickle')
pickle_file = list(pickle_files)[0]

# Extract job number from file name
node_num = re.match("^node_([0-9]+)_out.pickle$", pickle_file.name).groups(1)[0]
output_file = output_dir / f"node_{node_num}_in.pickle"

## Logging setup
#create a logger
logger = logging.getLogger(f'Node {node_num} Logger')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(log_file, mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# 


logger.debug(str(platform.uname()))
# Extract variables from pickle file
executor = dill.load(pickle_file.open('rb'))

# Delete all pickle files
logger.debug("Deleting all .pickle files")
[f.unlink() for f in pathlib.Path(resource_dir).glob('*.pickle')]

# Perform Simulation
# try:
raw_system_events, tensor_field, sessions = executor.execute()
# except Exception as e:
 #    logger.debug(e)

# Collect output variables
output_tuple = (raw_system_events,tensor_field,sessions)

# output_file.write_text('Test testing') #, str(len(list(pickle_files))))
#  
#  # Prep output file and write
output_file_handle = output_file.open('wb')
dill.dump(output_tuple, output_file_handle)
output_file_handle.close()
#  # 
