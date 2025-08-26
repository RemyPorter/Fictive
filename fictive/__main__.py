from .parser import *
from .states import Machine
from .print_helper import margined_print

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("filename")
parser.add_argument("-w", "--width", type=int, default=80)

args = parser.parse_args()

with open(Path(args.filename).resolve()) as f:
    loaded = load_yaml(f)
game,state_bag = parse(loaded)

margined_print(str(game.current()), args.width)
while(True):
    t,s = game.step(input("> "), state_bag)
    margined_print(str(s), args.width)
    if t == Machine.Result.End:
        print("Game Over!")
        break