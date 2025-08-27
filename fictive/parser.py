"""
Convert a dict (from YAML) into a state machine we can interact with.
"""

import io
from fictive.states import *
from fictive.triggers import *

# convert commands in YAML to functions in Python
TRIGGER_MAP = {
    "set_key": set_key,
    "on_match": on_match,
    "on_key": on_key,
    "on_all": on_all,
    "on_any": on_any,
    "revert": do_enter_revert,
    "on_gt": on_key_gt,
    "on_lt": on_key_lt,
    "inc": inc,
    "dec": dec
}


def parse_function(entry):
    """
    Parse a function entry from YAML. Function entries can have two forms.

    First:
    ```
    event_name:
        funcName:
            param1: value
            param2: value
    ```
    Or:
    ```
    event_name: funcName
    ```
    The difference between the two options is whether the function
    takes parameters or not. In the former, they're passed as kwargs.

    """
    if (isinstance(entry, dict)):  # this has kwargs parameters
        fname = list(entry.keys())[0]
        f = TRIGGER_MAP[fname]
        return f(**entry[fname])
    else:
        fname = entry  # this does not
        f = TRIGGER_MAP[fname]
        return f()


def parse_trigger(tag: str, state_desc: dict):
    """
    Parse an event (`tag`) and the associated functions for it

    Handles `on_enter`, `on_exit`
    """
    if tag in state_desc:
        section = state_desc[tag]
        if isinstance(section, list):
            fs = [parse_function(f) for f in section]
            return on_all(*fs)
        return parse_function(section)
    return lambda a, b, c: None


def parse_state(state_desc: dict):
    """
    Read a state entry out of the file, and construct a state object.

    Allows for sub-state machines embedded within this state.
    """
    tag = state_desc["tag"]
    descr = state_desc["description"]
    on_enter = parse_trigger("on_enter", state_desc)
    on_exit = parse_trigger("on_exit", state_desc)
    sub_machine = None
    if "sub_machine" in state_desc:
        sub_machine = parse_machine(state_desc["sub_machine"])
    # todo, add support for linking submachines
    return tag, State(descr, on_enter, on_exit, sub_machine)


def parse_transition(entry: dict, machine: MachineDesc, is_global=False):
    """
    Parse a transition and add it to a machine description. `is_global` creates a global
    transition which can apply anywhere.
    """
    on_handler = entry["condition"]
    if isinstance(on_handler, list):
        fs = [parse_function(f) for f in on_handler]
        on_cbk = on_all(*fs)
    else:
        on_cbk = parse_function(on_handler)
    if not is_global:
        machine.link(entry["from"], entry["to"], on_cbk)
    else:
        machine.global_link(entry["to"], on_cbk)


def parse_machine(entry: dict):
    """
    Parse a machine entry. This creates all the states and transitions required for the machine
    to execute.
    """
    desc = MachineDesc()
    state_entries = entry["states"]
    transitions = entry["transitions"]
    if "global_transitions" in entry:
        global_trans = entry["global_transitions"]
    else:
        global_trans = []
    for s in state_entries:
        if "state" in s:
            parsed = parse_state(s["state"])
        else:
            parsed = parse_state(s)
        desc.add_state(*parsed)
    for t in transitions:
        if "transition" in t:
            parse_transition(t["transition"], desc)
        else:
            parse_transition(t, desc)
    for t in global_trans:
        if "transition" in t:
            parse_transition(t["transition"], desc, True)
        else:
            parse_transition(t, desc, True)
    start_tag = entry["startTag"]
    if "endTag" in entry:
        end_tag = entry["endTag"]
    else:
        end_tag = ""
    return Machine(desc, start_tag, end_tag)


def parse(machine_desc: list):
    """
    Parse a yaml file. We expect a YAML array of dicts. The two sub-dicts we care about are 
    "exectue"- the machine definition we want to run, and "state_bag", the initial dictionary for
    the game.
    """
    state_bag = {}
    for entry in machine_desc:
        if "execute" in entry:
            main_entry = entry["execute"]
            machine = parse_machine(main_entry)
        if "state_bag" in entry:
            state_bag = entry["state_bag"]

    return machine, state_bag
