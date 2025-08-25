from fictive.triggers import *
from fictive.states import *
from fictive.parser import *

with open("game.yaml") as f:
    y = load_yaml(f)
game, state_bag = parse(y)


def prompt():
    print("> ", end="")
    return input()


print(game.current())
while (game.step(prompt(), state_bag) != Machine.Result.End):
    print(game.current())
print(game.current())
# go = r"(go|g|use)\s"
# n = r"(n|north)"
# take = r"(get|take)\s(.+)"
# flip = r"(flip|toggle|switch).*"

"""
switch_off = state("switch_off") \
    .description("There is a switch here. It is in the off position.")\
    .on_enter(set_key("switch", False)).state()
switch_on = state("switch_on") \
    .description("The switch is on. You hear a faint humming sound.")\
    .on_enter(set_key("switch", True)).state()

swim = MachineDesc().add_state(*switch_off).add_state(*switch_on)\
    .link("switch_off", "switch_on", on_match(flip))\
    .link("switch_on", "switch_off", on_match(flip))\
    switched = Machine(swim, "switch_off")

entry = state("entry") \
    .description("You are in a mysterious room. It's hard to say what's so mysterious about it, but that's the mystery.")\
    .sub_machine(switched)\
    .state()
midoff = state("middle_off") \
    .description("In this room, there is a large archway. Huge cables run into it. It is off.")\
    .state()
midon = state("middle_on") \
    .description("The large archway is crackling with energy. The cables glow with power. You want to walk into it")\
    .state()
ending = state("exit")\
    .description("You are in a less mysterious room. A bright red exit sign show that you've escaped.")\
    .state()
game = MachineDesc().add_state(*entry).add_state(*midoff).add_state(*midon).add_state(*ending)\
    .link("entry", "middle_off", on_all(on_match("leave"), on_key("switch", False)))\
    .link("entry", "middle_on", on_all(on_match("leave"), on_key("switch", True)))\
    .link("middle_off", "entry", on_match("(back|go back|return)"))\
    .link("middle_on", "exit", on_match("(enter|arch|exit)"))
m = Machine(game, "entry", "exit")


sb = {"switch": False}
print(m.current())
inp = input()
while (m.step(inp, sb) != Machine.Result.End):
    print(m.current())
    inp = input()
print(m.current())
"""
