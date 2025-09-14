"""
Convert a dict (from YAML) into a state machine we can interact with.
"""

import io
from fictive.states import *
from fictive.triggers import *
from functools import partial
from typing import Dict, Callable, Iterable
from itertools import chain

# convert commands in YAML to functions in Python
# the more verbose ones are in here as legacy support
# (for just me, but I've already built some code which uses them),
# but they all have shorter synonyms now
TRIGGER_MAP: Dict[str, Callable] = {
    "set_key": set_key,
    "set": set_key,
    "on_match": on_match,
    "match": on_match,
    "on_key": on_key,
    "tag": on_tag,
    "eq": on_key,
    "on_all": on_all,
    "all": on_all,
    "on_any": on_any,
    "any": on_any,
    "revert": do_enter_revert,
    "on_gt": on_key_gt,
    "gt": on_key_gt,
    "on_lt": on_key_lt,
    "lt": on_key_lt,
    "on_gte": on_key_gte,
    "gte": on_key_gte,
    "on_lte": on_key_lte,
    "lte": on_key_lte,
    "inc": inc,
    "dec": dec,
    "always": always,
    "banner": partial(set_key, "state.banner"),
    "subbanner": partial(set_key, "sub.banner"),
    "transbanner": partial(set_key, "trans.banner")
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
    if (isinstance(entry, dict)):  # this has parameters
        fname = list(entry.keys())[0]
        vals = entry[fname]
        f = TRIGGER_MAP[fname.lower()]
        if isinstance(vals, dict):  # kwargs
            return f(**vals)
        elif isinstance(vals, list):  # list of args
            return f(*vals)
        else:
            return f(vals)
    else:
        fname = entry  # this does not
        f = TRIGGER_MAP[fname.lower()]
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
    return State(tag, descr, on_enter, on_exit, sub_machine)

def _flatten(l: Iterable) -> Iterable:
    """
    To help organizing your games, we want to be able to nest states inside of the state array,
    so this will flatten them so we don't have to worry about how we do it.
    """
    for i in l:
        if isinstance(i, Iterable) and not isinstance(i, (str, bytes, dict)):
            yield from _flatten(i)
        else:
            yield i


def _peel(obj: dict, key: str):
    """Helper function to peel extraneous keys from our YAML entries"""
    if key in obj:
        return obj[key]
    return obj

def parse_condition(entry: dict):
    on_handler = _peel(entry, "condition")
    if isinstance(on_handler, list):
        fs = [parse_function(f) for f in on_handler]
        on_cbk = on_all(*fs)
    else:
        on_cbk = parse_function(on_handler)
    return on_cbk


def parse_transition(entry: dict, machine: MachineDesc, is_global=False):
    """
    Parse a transition and add it to a machine description. `is_global` creates a global
    transition which can apply anywhere.
    """
    on_handler = entry["condition"]
    on_cbk = parse_condition(entry)
    if not is_global:
        machine.link(entry["from"], entry["to"], on_cbk)
    else:
        machine.global_link(entry["to"], on_cbk)


def _handle_section(section: Iterable, handler: Callable) -> None:
    """Little cleanup for how we parse our various sections of a machine."""
    for s in section:
        handler(s)


def parse_machine(entry: dict):
    """
    Parse a machine entry. This creates all the states and transitions required for the machine
    to execute.
    """
    desc = MachineDesc()
    state_entries = _flatten(entry["states"])
    transitions = _flatten(entry["transitions"])
    global_trans = _flatten(entry.get("global_transitions", []))
    _handle_section(state_entries,
                    lambda s: desc.add_state(parse_state(_peel(s, "state"))))
    _handle_section(transitions,
                    lambda t: parse_transition(_peel(t, "transition"), desc))
    _handle_section(global_trans,
                    lambda g: parse_transition(_peel(g, "transition"), desc, True))
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
    title = "A Fictive Game"
    for entry in machine_desc:
        if "execute" in entry:
            main_entry = entry["execute"]
            machine = parse_machine(main_entry)
        if "state_bag" in entry:
            state_bag = entry["state_bag"]
        if "title" in entry:
            title = entry["title"]

    return machine, state_bag, title
