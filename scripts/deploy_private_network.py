#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import shutil
import time

import ansible.constants as C
from collections import namedtuple
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook import Playbook


# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        # print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result


def execute_playbook(play_book, host_list=[]):
    host_list = host_list
    # since the API is constructed for CLI it expects certain options to always be set in the context object
    context.CLIARGS = ImmutableDict(connection='smart', module_path=None, forks=None, become=None,
                                    become_method=None, become_user=None, check=False, diff=False)

    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','

    # initialize needed objects
    loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultsCollectorJSONCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultsCollectorJSONCallback()

    inventory = InventoryManager(loader=loader, sources=sources)
    
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
    )

    pbex = PlaybookExecutor(playbooks=[play_book], inventory=inventory, variable_manager=variable_manager, loader=loader, passwords=passwords)
    playbook = Playbook.load(pbex._playbooks[0], variable_manager=variable_manager, loader=loader)
    play = playbook.get_plays()[0]

    # Actually run it
    try:
        result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        tqm.cleanup()
        if loader:
            loader.cleanup_all_tmp_files()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
    
    # if(results_callback.host_ok.items()):
    #     print("********* SUCCESS ***********")
    #     return results_callback.host_ok.items()

    # if(results_callback.host_failed.items()):
    #     print("********* FAILED *******")
    #     for host, result in results_callback.host_failed.items():
    #         print('{0} >>> {1}'.format(host, result._result['msg'])) 

    # if(results_callback.host_unreachable.items()):
    #     print("********* HOST DOWN *********")
    #     for host, result in results_callback.host_unreachable.items():
    #         print('{0} >>> {1}'.format(host, result._result['msg']))


def create_node():
    return execute_playbook('../test/ec2.yml')

def main():
    results = create_node()
    for host, result in results:
        print(result)    
        instance_details=result._result["instances"][0]
    if(instance_details):
        print('Private IP {0} \nPublic IP {1}'.format(instance_details["private_ip"], instance_details["public_ip"]))
        print('Deploying besu private network') 
        time.sleep(20)
        results = execute_playbook('../test/besunet.yml', [instance_details["public_ip"]])

    

if __name__ == '__main__':
    main()