from .ui import FictiveUI
import asyncio

import argparse
from pathlib import Path
from .loader import load_game_yaml
from .parser import parse


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("game_dir", type=str, default="games",
                    help="The path to your collection of games.")
parser.add_argument("--debug", "-d", action="store_true",
                    help="Enable debugging features")
parser.add_argument("--test", "-t", action="store_true",
                    help="Test the loading of a game from a gamedir, without running it in the UI")
args = parser.parse_args()

if args.test:
    breakpoint() # yes, this is intentional. The test flag is developer only, so 
                 # while we wait for having better dev tools, this is it.
    loaded = load_game_yaml(args.game_dir)
    parsed = parse(loaded)
    exit(0)


async def game_loop():
    ui = FictiveUI(args.game_dir, debug=args.debug)
    loop = ui.run_async()
    await loop
asyncio.run(game_loop())
