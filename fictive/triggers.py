from .states import State, Machine
from re import Pattern, compile, IGNORECASE
from typing import Dict, List, Callable

Statebag = Dict[str, str]
Matcher = Callable[[State, str, Statebag], bool]


def set_key(key: str, value: str):
    def _m(current: State, inp: str, statebag: Statebag) -> bool:
        statebag[key] = value
        return True
    return _m


def on_match(matcher: Pattern | str, keys: List[str] = None):
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
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        return key in statebag and statebag[key] == value
    return _m


def always():
    def _m(current: State, inp: str, statebag: Dict[str, str]):
        return True
    return _m


def on_all(*fs: List[Matcher]):
    def _m(current: State, inp: str, statebag: Statebag):
        return all([f(current, inp, statebag) for f in fs])
    return _m


def on_any(*fs: List[Matcher]):
    def _m(current: State, inp: str, statebag: Statebag):
        return any([f(current, inp, statebag) for f in fs])
    return _m


def do_enter_revert():
    def _m(current: State, inp: str, statebag: Statebag):
        raise Machine.EnterAndRevert()
    return _m
