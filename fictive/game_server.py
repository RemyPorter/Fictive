"""
Create a factory system for making game objects, which
frees our game UI from worrying about the object life cycle.

It encapsulates both the game state and the state_bag within
itself, revealing only the bits that outside elements need.
"""
from .states import Machine, Statebag
from typing import Tuple, Dict

class GameServer:
    """
    Container for a game.
    """
    class NotStarted(Exception):
        pass

    _machine: Machine
    _bag: Statebag
    _started:bool = False

    def start(self, machine:Machine, bag:Statebag):
        self._machine = machine
        self._bag = bag
        self._machine.start(bag)
        self._started = True

    def tick(self, inp:str) -> Tuple[Machine.StepResult, Statebag]:
        if not self._started:
            raise GameServer.NotStarted()
        ticked = self._machine.step(inp, self._bag)
        return ticked, self.bag() # give clients copies of our statebag

    def bag(self):
        return self._bag.copy()

    def current(self):
        return self._machine.current()

# a lookup table to allow us to manage multiple running games at the same time
_server: Dict[str, GameServer] = {"default": GameServer()}

def get_game_server(key:str="default"):
    """
    Return an instance of a game server, which lets clients
    then run the game.
    """
    if key not in _server:
        _server[key] = GameServer()
    return _server[key]
