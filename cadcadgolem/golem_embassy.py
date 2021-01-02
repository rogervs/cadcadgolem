import asyncio
from datetime import timedelta
import pathlib
import sys
import dill
import os
import subprocess
import json

TEXT_COLOR_YELLOW = "\033[33;1m"
TEXT_COLOR_DEFAULT = "\033[0m"

script_dir = pathlib.Path(__file__).resolve().parent
pickle_dir = script_dir / 'pickles'
remote_exec_dir = script_dir / 'remote'
remote_env_file = 'run-golem-diplomat.sh'
remote_exec_file = 'golem-diplomat.py'
remote_log_dir = remote_exec_dir / 'logs'
remote_env_path = remote_exec_dir / remote_env_file
remote_exec_path = remote_exec_dir / remote_exec_file
gol_work_dir = pathlib.Path('/golem/work')
gol_env_path = gol_work_dir / remote_env_file

location_dict = {
        "script_dir" : str(script_dir),
        "pickle_dir" : str(pickle_dir),
        "remote_exec_dir" : str(remote_exec_dir),
        "remote_env_file" : str(remote_env_file),
        "remote_exec_file" : str(remote_exec_file),
        "remote_log_dir" : str(remote_log_dir),
        "remote_env_path" : str(remote_env_path),
        "remote_exec_path" : str(remote_exec_path),
        "gol_work_dir" : str(gol_work_dir),
        "gol_env_path" : str(gol_env_path),
}
            
def Ambassador(func, golem_conf):
    # Decorator factory
    def wrapper(*args, **kwargs):
        golem_nodes = dict()
        # Split configs up between the nodes
        for node in range(golem_conf['NODES']):
            temp_configs = kwargs['configs'][node::golem_conf['NODES']]
            golem_nodes[node]={
                    'exec_context': kwargs['exec_context'],
                    'configs':temp_configs
                    }

        # Create pickles for transfer to network later on
        if not pickle_dir.exists():
            pickle_dir.mkdir()
        else:
            [x.unlink() for x in pickle_dir.iterdir()]
        for node in golem_nodes:
            golem_nodes[node]['executor'] = func(**golem_nodes[node])
            filename = pickle_dir / ("node_"+str(node)+"_out.pickle")

            dill_out = filename.open("wb")
            dill.dump(golem_nodes[node]['executor'], dill_out)
            dill_out.close()

        def golem_diplomat(golem_conf):
            print(
                f"{TEXT_COLOR_YELLOW}"
                f"Initiating Communication with Golem Network"
                f"{TEXT_COLOR_DEFAULT}"
            )

            subprocess.call([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)])



        def golem_reconstruct(self):
            # Load data files received back from Golem network
            for node in golem_nodes:
                filename = pickle_dir / ("node_"+str(node)+"_in.pickle")
                file_in = filename.open("rb")
                dill_load = dill.load(file_in)
                file_in.close()
                golem_nodes[node]['output'] = dill_load

            # Reasemble output from files
            output_length = 3 # Number of elements in the output tuple
            output = dict()

            for i in range(output_length):
                temp = []
                for node in golem_nodes:
                    temp += golem_nodes[node]['output'][i]
                output[i] = temp

            a = output[0]
            b = output[1]
            c = output[2]

            return a, b, c

        def golem_execute(self, *args, **kwargs):
            golem_diplomat(golem_conf)
            return golem_reconstruct(self)

        func.execute = golem_execute

        return_value = func(*args, **kwargs)
        return return_value

    return wrapper

