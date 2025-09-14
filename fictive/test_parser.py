"""
Convert a YAML file into a test script to execute against a game.
"""

from .parser import TRIGGER_MAP, parse_condition, _peel, _flatten, Matcher
from .game_server import get_game_server
from .states import Machine, Statebag
from typing import Callable, List
from dataclasses import dataclass

TestCallback = Callable[[str], bool]

class Assertion:
    """An assertion in YAML"""
    def __init__(self, cbk:Matcher):
        self.assertion = cbk

    def __call__(self, testTag:str)->bool:
        g = get_game_server(testTag)
        return self.assertion(g.current(), "", g.bag())

class Input:
    """An input command in YAML"""
    def __init__(self, text:str):
        self.text = text

    def __call__(self, testTag:str)->bool:
        g = get_game_server(testTag)
        (step, _) = g.tick(self.text)
        # Errors represent unworkable states in fictive,
        # so we don't need to worry about testing error handling
        # these should never happen- a test fails in this case
        return step.action != Machine.Result.Error 
        
class BadTestStep(Exception):
    """Parsing failed"""
    pass

class GameTest:
    """
    A test for a game, which is a series of `Input`s and `Assertion`s.
    """
    def __init__(self, tag:str):
        self.tag = tag
        self.steps:List[TestCallback] = []

    def add_step(self, step:TestCallback):
        """Add a step to our test run"""
        self.steps.append(step)

    def __iadd__(self, step:TestCallback):
        """+= to add a step to our test run"""
        self.steps.append(step)
        return self

    def run(self, machine:Machine, bag:Statebag)->List[bool]:
        """Run the test against a game server"""
        get_game_server(self.tag).start(machine, bag.copy())
        step_results:List[bool] = []
        for i,step in enumerate(self.steps):
            res = step(self.tag)
            step_results.append(res)
        return step_results

def parse_test_line(entry:dict)->Assertion|Input:
    """Read a line into an Assertion of Input"""
    if "assert" in entry:
        return Assertion(parse_condition(_peel(entry, "assert")))
    elif "input" in entry:
        return Input(entry["input"])
    raise BadTestStep(str(entry))

def parse_test(test_name, entry:dict)->GameTest:
    """Read an entire test into a GameTest"""
    gt = GameTest(test_name)
    for step in entry.get("steps", []):
        gt += parse_test_line(step)
    return gt

