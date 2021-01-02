import numpy as np
from cadCAD.configuration import Experiment
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Configuration
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor
import pandas as pd
from cadcadgolem.golem_embassy import Ambassador


# Most of this code comes from https://github.com/cadCAD-org/snippets


def p_something(params,
                substep,
                state_history,
                prev_state):
    parameter = params['parameter']
    random_value_1 = np.random.randn() + parameter
    random_value_2 = np.random.rand() + parameter
    return {'policy_input_1': random_value_1,
            'policy_input_2': random_value_2}


def s_something(params,
                substep,
                state_history,
                prev_state,
                policy_input):
    new_value = policy_input['policy_input_1']
    new_value += policy_input['policy_input_2']
    return ('something', new_value)


partial_state_update_blocks = [
    {
        'policies': {
            'something': p_something

        },
        'variables': {
            'something': s_something
        }
    }
]

from cadCAD import configs
del configs[:]

MONTE_CARLO_RUNS = 20
SIMULATION_TIMESTEPS =200 

sys_params = {
    'parameter': [0.1, 0.2, 0.3],
}

genesis_states = {
    'something': 0
}


sim_config = {
    'N': MONTE_CARLO_RUNS,
    'T': range(SIMULATION_TIMESTEPS),
    'M': sys_params
}

sim_params = config_sim(sim_config)

exp = Experiment()
exp.append_configs(
    sim_configs=sim_params,
    initial_state=genesis_states,
    partial_state_update_blocks=partial_state_update_blocks
)




golem_conf = {
        'NODES': 3, # Number of nodes to utilise from the Golem Network. If you've got a big simulation to run, try pushing this up to 30. Remember you need at least twice as many simulation runs as you have nodes.
        'BUDGET': 10.0, # Maximum amount of crypto you are prepared to spend
        'SUBNET': "community.3", # choose your subnet, currently this is the test network
#         'SUBNET': 'devnet-alpha.3',
        'YAGNA_APPKEY': '8a5e4a8b9023406ea7a770010b2d513a', # get this from `yagna app-key list`

        'TIMEOUT': 120 # In seconds - you will need to figure this out for your workload. Max currently is 25min, so 25 * 60 seconds
        }

Executor = Ambassador(Executor, golem_conf)
exec_context = ExecutionContext(context=ExecutionMode.single_mode )
simulation = Executor(exec_context=exec_context, configs=configs)
#simulation = Executor(exec_context=local_mode_ctx, configs=configs)


raw_system_events, tensor_field, sessions = simulation.execute()

df = pd.DataFrame(raw_system_events)


print(df)

