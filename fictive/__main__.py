from .ui import FictiveUI
import asyncio

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)
parser.add_argument("game_dir", type=str, default="games", help="The path to your collection of games.")
args = parser.parse_args()

async def game_loop():
    ui = FictiveUI(args.game_dir)
    loop = ui.run_async()
    await loop
asyncio.run(game_loop())


