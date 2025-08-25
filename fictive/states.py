from dataclasses import dataclass
from typing import Callable, Dict, List
from enum import Enum

Statebag = Dict[str, str]
StateCallback = Callable[[str, Statebag], None]
TransitionCallback = Callable[["State", str, Statebag], bool]


class State:
    def __init__(self, description: str, on_enter: StateCallback = None,
                 on_exit: StateCallback = None, sub_machine: "Machine" = None):
        self._descr = description
        if on_enter:
            self._on_enter = on_enter
        else:
            self._on_enter = lambda inp, bag: None
        if on_exit:
            self._on_exit = on_exit
        else:
            self._on_exit = lambda inp, bag: None
        self._sub = sub_machine

    def sub(self):
        return self._sub

    def __str__(self):
        res = self._descr
        if self._sub and self._sub.current():
            res += "\n"
            res += str(self._sub.current())
        return res


@dataclass
class Transition:
    orig: State
    dest: State
    condition: TransitionCallback


class state:
    def __init__(self, tag: str):
        self._tag = tag
        self._descr = ""
        self._buildable = False
        self._on_enter = lambda s, i, b: True
        self._on_exit = lambda s, i, b: True
        self._sub_m = None

    def description(self, description: str):
        self._descr = description
        self._buildable = True
        return self

    def on_enter(self, on_enter: StateCallback):
        self._on_enter = on_enter
        return self

    def on_exit(self, on_exit: StateCallback):
        self._on_exit = on_exit
        return self

    def sub_machine(self, sub: "Machine"):
        self._sub_m = sub
        return self

    def state(self):
        return self._tag, State(self._descr, self._on_enter, self._on_exit, self._sub_m)


class MachineDesc:
    def __init__(self):
        self._states: Dict[str, State] = {"": State("")}
        self._rstates: Dict[State, str] = {}
        self._transitions: Dict[str, List[Transition]] = {}
        self._global_transitions: List[Transition] = []

    def add_state(self, tag: str, s: State):
        self._states[tag] = s
        self._rstates[s] = tag
        self._transitions[tag] = []
        return self

    def link(self, tagOrigin: str, tagDest: str, cbk: TransitionCallback):
        o = self._states[tagOrigin]
        d = self._states[tagDest]
        self._transitions[tagOrigin].append(Transition(o, d, cbk))
        return self

    def global_link(self, tagDest: str, cbk: TransitionCallback):
        o = None
        d = self._states[tagDest]
        self._global_transitions.append(Transition(o, d, cbk))
        return self

    def __getitem__(self, idx: str):
        return self._states[idx]


class Machine:
    class Result(Enum):
        NoChange = 0
        Transitioned = 1
        Rejected = 2
        End = 3

    class RejectWithMessage(Exception):
        def __init__(self, msg: str):
            self._msg = msg

        def __str__(self):
            return self._msg

    class EnterAndRevert(Exception):
        pass

    def __init__(self, mach: MachineDesc, startTag: str, endTag: str = ""):
        self._internal = mach
        self._start = mach[startTag]
        self._end = mach[endTag]
        self._current = startTag

    def current(self) -> State:
        return self._internal[self._current]

    def step(self, inp: str, state_bag: Dict[str, str] = None) -> Result:
        if state_bag is None:
            state_bag = {}
        curr = self.current()
        sub_trans = Machine.Result.NoChange
        # check substates
        if curr.sub():
            sub_trans = curr.sub().step(inp, state_bag)
        for t in self._internal._transitions[self._current] + self._internal._global_transitions:
            transed = t.condition(curr, inp, state_bag)
            if transed:
                try:
                    curr._on_exit(curr, inp, state_bag)
                    t.dest._on_enter(curr, inp, state_bag)
                except Machine.RejectWithMessage as ex:
                    print(ex.msg)
                    return Machine.Result.Rejected
                except Machine.EnterAndRevert:
                    print(t.dest, "\n")
                    return Machine.Result.NoChange
                except:
                    return Machine.Result.Rejected
                next_s = t.dest
                next_t = self._internal._rstates[next_s]
                self._current = next_t
                if next_s == self._end:
                    return Machine.Result.End
                return Machine.Result.Transitioned
        return sub_trans
