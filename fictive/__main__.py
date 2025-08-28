from .ui import FictiveUI
import asyncio

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog="Fictive Interactive Fiction Runtime",
    description="Load and run Fictive style games"
)

async def game_loop():
    ui = FictiveUI()
    loop = ui.run_async()
    await loop
asyncio.run(game_loop())


