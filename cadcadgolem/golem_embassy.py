#!/usr/bin/env python3
import asyncio
from datetime import timedelta
import pathlib
import sys
import dill
import os

from yapapi import (
    Executor,
    Task,
    __version__ as yapapi_version,
    WorkContext,
    windows_event_loop_fix,
)
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm
from yapapi.rest.activity import BatchTimeoutError

TEXT_COLOR_RED = "\033[31;1m"
TEXT_COLOR_GREEN = "\033[32;1m"
TEXT_COLOR_YELLOW = "\033[33;1m"
TEXT_COLOR_BLUE = "\033[34;1m"
TEXT_COLOR_MAGENTA = "\033[35;1m"
TEXT_COLOR_CYAN = "\033[36;1m"
TEXT_COLOR_WHITE = "\033[37;1m"
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

async def main(run_conf: dict):
    package = await vm.repo(
        image_hash="a885ed794412c27dedb49d52181ca6ea1a6f4e69b3cce365f1020966",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        async for task in tasks:
            node = task.data

            # Set various file locations
            output_file = str(pickle_dir / f"node_{node}_in.pickle")
            log_file = str(remote_log_dir / f"node_{node}.log")
            sh_log_file = str(remote_log_dir / f"node_{node}_sh.log")
            pickle_path = str(pickle_dir / f"node_{node}_out.pickle")

            # Send data, environment shell script, and execution script
            ctx.send_file(pickle_path, f"/golem/resource/node_{node}_out.pickle")
            ctx.send_file(remote_env_path , f"/golem/work/{remote_env_file}")
            ctx.send_file(remote_exec_path , f"/golem/work/{remote_exec_file}")

            # /dev/shm is needed for python multiprocessing
            ctx.run("/bin/mkdir", "-p", "/dev/shm")
            ctx.run("/bin/mount", "-t", "tmpfs", "tmpfs", "/dev/shm") 
            commands = (
                 f'chmod a+x {remote_env_file}; '
                 f'./{remote_env_file}; '
            )
            ctx.run("/bin/sh", "-c", commands)
            
            # Pull logs and data
            ctx.download_file(f"/golem/output/node_{node}_in.pickle", output_file)
            ctx.download_file("/golem/output/output.log", log_file)
            ctx.download_file("/golem/output/sh.log", sh_log_file)

#            yield ctx.commit(timeout=timedelta(seconds=120))
#            task.accept_result(result=log_file)
#            task.accept_result(result=sh_log_file)
            try:
                # Set timeout for executing the script on the provider. Two minutes is plenty
                # of time for computing a single frame, for other tasks it may be not enough.
                # If the timeout is exceeded, this worker instance will be shut down and all
                # remaining tasks, including the current one, will be computed by other providers.
                yield ctx.commit(timeout=timedelta(seconds=120))
                # TODO: Check if job results are valid
                # and reject by: task.reject_task(reason = 'invalid file')
                task.accept_result(result=output_file)
            except BatchTimeoutError:
                print(
                    f"{TEXT_COLOR_RED}"
                    f"Task timed out: {task}, time: {task.running_time}"
                    f"{TEXT_COLOR_DEFAULT}"
                )
                raise

    # Iterator over the amount blocks (amount of nodes) that we have selected
    nodes: range = range(run_conf['NODES'])
    # Worst-case overhead, in minutes, for initialization (negotiation, file transfer etc.)
    # TODO: make this dynamic, e.g. depending on the size of files to transfer
    init_overhead = 3
    # Providers will not accept work if the timeout is outside of the [5 min, 30min] range.
    # We increase the lower bound to 6 min to account for the time needed for our demand to
    # reach the providers.
    min_timeout, max_timeout = 6, 30

#    timeout = timedelta(minutes=max(min(init_overhead + len(nodes) * 2, max_timeout), min_timeout))
    timeout = timedelta(minutes=min_timeout)

    # By passing `event_consumer=log_summary()` we enable summary logging.
    # See the documentation of the `yapapi.log` module on how to set
    # the level of detail and format of the logged information.
    async with Executor(
        package=package,
        max_workers=run_conf['NODES'],
        budget=run_conf['BUDGET'],
        timeout=timeout,
        subnet_tag=run_conf['SUBNET'],
        #run_conf['subnet_tag'],
        event_consumer=log_summary(log_event_repr),
    ) as executor:

        async for task in executor.submit(worker, [Task(data=node) for node in nodes]):
            print(
                f"{TEXT_COLOR_CYAN}"
                f"Task computed: {task}, result: {task.result}, time: {task.running_time}"
                f"{TEXT_COLOR_DEFAULT}"
            )


            
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
            


        def golem_diplomat(self, *args, **kwargs):
            os.environ['YAGNA_APPKEY'] = golem_conf['YAGNA_APPKEY']
            description = "cadCAD Simulation"
            yapapi_log_file="cadcad-yapapi.log"

            # This is only required when running on Windows with Python prior to 3.8:
            windows_event_loop_fix()

            enable_default_logger(log_file=yapapi_log_file)

            loop = asyncio.get_event_loop()

            subnet = golem_conf['SUBNET']


            sys.stderr.write(
                    f"yapapi version: {TEXT_COLOR_YELLOW}{yapapi_version}{TEXT_COLOR_DEFAULT}\n"
                    )
            sys.stderr.write(f"Using subnet: {TEXT_COLOR_YELLOW}{golem_conf['SUBNET']}{TEXT_COLOR_DEFAULT}\n")

            #print("run_conf prior :", golem_conf)
            # run_conf = {
            #         'subnet_tag': subnet,
            #         'node_count': 3,
            #         'budget': 10.0
            #         }
            # print("run_conf post :", run_conf)


            task = loop.create_task(main(run_conf=golem_conf))
            try:
                loop.run_until_complete(task)
            except KeyboardInterrupt:
                print(
                        f"{TEXT_COLOR_YELLOW}"
                        "Shutting down gracefully, please wait a short while "
                        "or press Ctrl+C to exit immediately..."
                        f"{TEXT_COLOR_DEFAULT}"
                        )
                task.cancel()
                try:
                    loop.run_until_complete(task)
                    print(
                            f"{TEXT_COLOR_YELLOW}"
                            "Shutdown completed, thank you for waiting!"
                            f"{TEXT_COLOR_DEFAULT}"
                            )
                except (asyncio.CancelledError, KeyboardInterrupt):
                    pass

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
            golem_diplomat(self, *args, **kwargs)
            return golem_reconstruct(self)


        func.execute = golem_execute


        return_value = func(*args, **kwargs)
        return return_value

    return wrapper

