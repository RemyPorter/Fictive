from .ui import FictiveUI
import asyncio

import argparse
from pathlib import Path
from .loader import load_game_yaml, load_test
from .parser import parse
from .test_parser import parse_test
from .test_runner import test_main


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("game_dir", type=str, default="games",
                    help="The path to your collection of games.")
parser.add_argument("--debug", "-d", action="store_true",
                    help="Enable debugging features")
parser.add_argument("--test_game", "-t", type=str, default=None,
                    help="Load a game and run its test suite, without loading the UI")
args = parser.parse_args()

if args.test_game:
    gut = Path(args.game_dir) / Path(args.test_game)
    loaded = load_game_yaml(gut)
    machine,statebag,title = parse(loaded)
    test_defs = []
    for l in loaded[::-1]: # in parsing, we favor putting the tests at the end
        if "tests" in l:
            for t in l["tests"]:
                test_main(loaded, gut)
                
    exit(0)



async def game_loop():
    ui = FictiveUI(args.game_dir, debug=args.debug)
    loop = ui.run_async()
    await loop
asyncio.run(game_loop())
