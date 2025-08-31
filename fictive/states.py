from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, TypeAlias, Optional
from enum import Enum

Statebag = Dict[str, str]|None
StateCallback = Callable[["State", str, Statebag], None]
OptionalStateCallback:TypeAlias = StateCallback|None
TransitionCallback = Callable[["State", str, Statebag], bool]
OptionalTransitionCallback = TransitionCallback|None
Mach=Optional["Machine"]

def null_state_callback(_state:"State", _inp:str,_bag:Statebag)->None:
    pass

class State:
    """
    One state in our game's state machine. This is the key object we have in the system.
    The goal of the game is for the player no navigate through states by issuing commands.

    A state must have a description, which is the text we will display to the user.

    A state may have an `on_enter` and `on_exit` event function.

    A state may also have a `sub_machine`, a state machine of substates. You can
    theoretically nest substate machines as much as you like. Practically, that would be
    very difficult to write effectively.
    """
    def __init__(self, description: str, on_enter: OptionalStateCallback = None,
                 on_exit: OptionalStateCallback = None, sub_machine: Mach = None):
        self._descr = description
        if on_enter:
            self._on_enter:StateCallback = on_enter
        else:
            self._on_enter = null_state_callback
        if on_exit:
            self._on_exit:StateCallback = on_exit
        else:
            self._on_exit = null_state_callback
        self._sub = sub_machine

    def sub(self):
        return self._sub

    def description(self):
        return self._descr

    def __str__(self):
        res = self._descr
        if self._sub and self._sub.current():
            res += "\n"
            res += str(self._sub.current())
        return res

    def substates(self):
        if not self._sub:
            return []
        res = [self._sub.current().description()]
        res += self._sub.current().substates()
        return res




@dataclass
class Transition:
    """
    Holder for a transition. Where wo go from, where we go to,  when we go.
    """
    orig: State|None
    dest: State
    condition: TransitionCallback

class MachineDesc:
    """
    The static description of a machine. 

    It contains:
        * a list of states organized by tags
            * a reverse lookup to go from a state to its tag
        * a collection of transitions, organized by tag
        * a collection of global transitions, which are always active
    """
    def __init__(self):
        self._states: Dict[str, State] = {"": State("")}
        self._rstates: Dict[State, str] = {}
        self._transitions: Dict[str, List[Transition]] = {}
        self._global_transitions: List[Transition] = []

    def add_state(self, tag: str, s: State):
        """
        Add a state to this machine
        """
        self._states[tag] = s
        self._rstates[s] = tag
        self._transitions[tag] = []
        return self

    def link(self, tagOrigin: str, tagDest: str, cbk: TransitionCallback):
        """
        Create a link between two states. Note we use the tags of the states,
        not the state objects themselves. This is more user friendly for our
        fiction developers.
        """
        o = self._states[tagOrigin]
        d = self._states[tagDest]
        self._transitions[tagOrigin].append(Transition(o, d, cbk))
        return self

    def global_link(self, tagDest: str, cbk: TransitionCallback):
        """
        Create a global state transition. 
        """
        o = None
        d = self._states[tagDest]
        self._global_transitions.append(Transition(o, d, cbk))
        return self

    def __getitem__(self, idx: str):
        return self._states[idx]


class Machine:
    """
    The actual executing state machine. Manages the iteration across all our states.
    """
    class Result(Enum):
        NoChange = 0
        Transitioned = 1
        Rejected = 2
        End = 3
        Transient = 4
        Error = 5

    class RejectWithMessage(Exception):
        def __init__(self, msg: str):
            self._msg = msg

        def __str__(self):
            return self._msg

    class EnterAndRevert(Exception):
        pass

    @dataclass
    class StepResult:
        action: "Machine.Result"
        state: State
        transient: State|None
        additionalMessages: str|None = None


    def __init__(self, mach: MachineDesc, startTag: str, endTag: str = ""):
        self._internal = mach
        self._start = mach[startTag]
        self._end = mach[endTag]
        self._current = startTag

    def current(self) -> State:
        return self._internal[self._current]

    def start(self, state_bag: Statebag):
        self.current()._on_enter(self.current(), "", state_bag)
        if self.current().sub():
            self.current().sub().current()._on_enter(self.current(), "", state_bag)

    def step(self, inp: str, state_bag: Statebag = None) -> "Machine.StepResult":
        """
        This function represents the main game loop, and this is the bit which needs the 
        most work.

        Given a user-supplied input and a state_bag, it checks all active state transitions
        for our current state, all its substates, and any global transitions. If a substate
        transition happens, we still allow a state transition to happen, meaning two 
        transitions could happen on the same input. However, if a state transition happens,
        a global transition WILL NOT.

        This is a choice- substate transitions often will alter the statebag, which means
        there are valid reasons why a developer might have a substate transition and a state
        transition consume the same input. Global transitions, on the other hand, are meant
        to be more transient. The idea here is you might check inventory, ask for help, or 
        something like that. So global transitions *usually* just `revert` back to the original
        state.

        TODO: a useful feature here would be a special `pop` transition, which allows us to 
        go back to a previous state. Especially useful for global transitions, which move us to
        states without respecting the state machine. On exiting a global transition, we may want to
        pop. Currently, the best way to do that is to revert.
        """
        if state_bag is None:
            state_bag = {}
        curr = self.current()
        sub_trans = Machine.Result.NoChange
        # check substates
        if curr.sub():
            sub_step = curr.sub().step(inp, state_bag)
            sub_trans = sub_step.action
        for t in self._internal._transitions[self._current] + self._internal._global_transitions:
            transed = t.condition(curr, inp, state_bag)
            if transed:
                # try to exit, and if we fail, abort transitions
                try:
                    curr._on_exit(curr, inp, state_bag)
                except Exception as ex:
                    return Machine.StepResult(Machine.Result.Rejected,
                        curr,
                        None,
                        str(ex))
                # try to enter, any failures fail to transition
                try:
                    t.dest._on_enter(curr, inp, state_bag)
                except Machine.RejectWithMessage as ex:
                    return Machine.StepResult(Machine.Result.Rejected, \
                        curr, None, ex._msg)
                except Machine.EnterAndRevert:
                    return Machine.StepResult(Machine.Result.Transient,\
                            curr, t.dest) 
                except Exception as err:
                    return Machine.StepResult(Machine.Result.Error, \
                        curr, t.dest, str(err))
                next_s = t.dest
                next_t = self._internal._rstates[next_s]
                self._current = next_t
                if next_s == self._end:
                    return Machine.StepResult(Machine.Result.End, self._end, None)
                return Machine.StepResult(Machine.Result.Transitioned, next_s, None)
        return Machine.StepResult(sub_trans, curr, None)
