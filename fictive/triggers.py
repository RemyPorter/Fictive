"""
These functions all represent helper functions to manage our state machine
transitions.
"""
from .states import State, Machine
from re import Pattern, compile, IGNORECASE
from typing import Dict, List, Callable

Statebag = Dict[str, str]
Matcher = Callable[[State, str, Statebag], bool]


def set_key(key: str, value: str):
    """
    Set a key in our statebag. Mostly used in on_enter or on_exit events.
    """
    def _m(current: State, inp: str, statebag: Statebag) -> bool:
        statebag[key] = value
        return True
    return _m

def _key_as_int(key:str, statebag:Statebag):
    try:
        return int(statebag[key])
    except:
        return 0

def inc(key: str):
    """
    Increment a key. If the current value is not an integer, it will be treated
    as zero.
    """
    def _m(current: State, inp: str, statebag: Statebag) -> bool:
        statebag[key] = _key_as_int(key, statebag) + 1
    return _m

def dec(key: str):
    """
    Decrement a key. If the current value is not an integer, it will be treated
    as zero.
    """
    def _m(current: State, inp: str, statebag: Statebag) -> bool:
        statebag[key] = _key_as_int(key, statebag) - 1
    return _m


def on_match(matcher: Pattern | str, keys: List[str] = None):
    """
    An on_match condition. Usually checked against input as part of a
    transition. Supports regexes. Precompiles the regex and captures it.
    """
    if isinstance(matcher, str):
        patt = compile(matcher, IGNORECASE)
    else:
        patt = matcher

    def _m(current: State, inp: str, statebag: Dict[str, str]):
        matched = patt.fullmatch(inp)
        if not matched:
            return False
        if keys:
            try:
                for k, v in zip(keys, matched.groups()):
                    statebag[k] = v
            except:
                pass
        return True
    return _m


def on_key(key: str, value: str):
    """
    Transition condition that checks a key in our statebag. Only supports equality checks.
    """
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        return key in statebag and statebag[key] == value
    return _m

def on_key_gt(key: str, value: str):
    """
    Transition condition that checks a key in our statebag. If it converts to int
    it uses a numeric comparison. Otherwise it's a textual comparison.
    """
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        if not key in statebag:
            return False
        try:
            v = int(statebag[key])
            return v > int(value)
        except:
            return statebag[key] > value
    return _m

def on_key_lt(key: str, value: str):
    """
    Transition condition that checks a key in our statebag. If it converts to int
    it uses a numeric comparison. Otherwise it's a textual comparison.
    """
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        if not key in statebag:
            return False
        try:
            v = int(statebag[key])
            return v < int(value)
        except:
            return statebag[key] < value
    return _m

def always():
    """
    Transition condition which always is true.
    """
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        return True
    return _m


def on_all(*fs: List[Matcher]):
    """
    Composite condition; only transition if ALL the subfunctions are true.
    """
    def _m(current: State, inp: str, statebag: Statebag):
        return all([f(current, inp, statebag) for f in fs])
    return _m


def on_any(*fs: List[Matcher]):
    """
    Composite condition; only transition if ANY of the subfunctions are true.
    """
    def _m(current: State, inp: str, statebag: Statebag):
        return any([f(current, inp, statebag) for f in fs])
    return _m


def do_enter_revert():
    """
    An on-enter event handler which immediately reverts the current state.

    This is mostly for global transitions; report a global state and transition
    right back to the state you left.
    """
    def _m(current: State, inp: str, statebag: Statebag):
        raise Machine.EnterAndRevert()
    return _m
