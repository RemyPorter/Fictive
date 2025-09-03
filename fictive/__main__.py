from .ui import FictiveUI
import asyncio

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("game_dir", type=str, default="games",
                    help="The path to your collection of games.")
parser.add_argument("--debug", "-d", action="store_true",
                    help="Enable debugging features")
args = parser.parse_args()


async def game_loop():
    ui = FictiveUI(args.game_dir, debug=args.debug)
    loop = ui.run_async()
    await loop
asyncio.run(game_loop())
