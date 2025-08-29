from .parser import *
from .states import Machine
from .print_helper import print_sections
from .loader import load_yaml
from .ui import UI, FictiveUI
import curses
from time import sleep
import asyncio

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("filename")
parser.add_argument("-w", "--width", type=int, default=80)

args = parser.parse_args()

loaded = load_yaml(Path(args.filename))
game, state_bag, title = parse(loaded)


async def game_loop():
    ui = FictiveUI()
    ui.title = title
    ui.game = game
    ui.state_bag = state_bag
    loop = ui.run_async()
    await loop


asyncio.run(game_loop())
"""
def main(stdscr):
    loaded = load_yaml(Path(args.filename))
    game, state_bag = parse(loaded)
    ui = UI()
    while True:
        inp = ui.update(game.current(), state_bag)
        t, s = game.step(inp, state_bag)
        if t == Machine.Result.End:
            print("Game Over!")
            break


curses.wrapper(main)
"""
