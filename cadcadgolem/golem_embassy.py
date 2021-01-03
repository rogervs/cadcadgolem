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
                f"===================================================================\n"
                f"Initiating Negotiations With Golem Network\n"
                f"===================================================================\n"
                f"Patience you must have.\n"
                f"See your Jupyter server terminal/log for realtime details\n"
                f"This is a good time to go think about what TIMEOUT you set.\n"
                f"If you are not in a hurry, or you just don't know, you can\n"
                f"set it up to 25 minutes.But note, that is 25 minutes per attempt.\n"
                f"A server could stall, and hold you there for 25 minutes,\n"
                f"before you let that workload go and go find another server.\n"
                f"To stop this, you will have to kill your Jupyter Server.\n"
                f"Just Ctrl-c (a few times) at the same place you're watching the logs.\n"
                f"===================================================================\n"
                f"{TEXT_COLOR_DEFAULT}"
            )

#            subprocess.call([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)])
#            proc = subprocess.Popen([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#            for line in proc.stdout:
#                print(line)
#
#            p = subprocess.Popen([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)], stdout=subprocess.PIPE, bufsize=1)
#            for line in iter(p.stdout.readline, b''):
#                print(line)
#            p.stdout.close()        
#            p.wait()

#            with subprocess.Popen([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)], stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
#                while True:
#                    try:
#                        line = p.stdout.readline()
#                    #if not line:
#                    except:
#                        break
#                    print(line)    
#                exit_code = p.poll()

            subprocess.run([sys.executable, script_dir / "async_isolation.py", json.dumps(golem_conf), json.dumps(location_dict)], bufsize=1, universal_newlines=True)   

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

