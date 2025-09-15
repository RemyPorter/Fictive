from ruamel.yaml import YAML
from pathlib import Path
from contextlib import ExitStack
from typing import List, Iterator, Tuple
from dataclasses import dataclass
from sys import stderr

yaml=YAML(typ='safe')   # default

def merge_game_yaml(root: Path, mfest:dict) -> str:
    """
    By reading the manifest, load all the files in that manifest and
    merge them into a single string so we can parse it in YAML.
    """

    files = [root / entry for entry in mfest["files"]]
    with ExitStack() as stack:
        read_from = [stack.enter_context(
            entry.open()).read() for entry in files]
    merged = "\n".join(read_from)
    return merged

def load_manifest(manifest:Path)->dict:
    if not manifest.exists():
        raise Exception("Invalid Game Directory")
    with manifest.open() as f:
        mfest = yaml.load(f)
        return mfest

def load_test(test_path:Path|str)->dict:
    p = Path(test_path).resolve()
    with p.open() as f:
        return yaml.load(f)

def load_game_yaml(gameInstance: Path | str):
    """
    Load a game from a directory, by scanning the `files` 
    entry in the manifest.
    """
    root = Path(gameInstance).resolve()
    manifest = root / "manifest.yaml"
    mfest = load_manifest(manifest)
    merged = merge_game_yaml(root, mfest)
    try:
        loaded = yaml.load(merged)
    except Exception as ex:
        print("Failed to load game, YAML error: ", file=stderr)
        bad_line = merged.split('\n')[ex.problem_mark.line]
        print(f"\t{ex.problem}: {bad_line}", file=stderr)
    return loaded | mfest

@dataclass
class GameListEntry:
    """Helper class to keep track of the games in our gamedir"""
    title:str
    slug:str
    author:str
    path:Path

def load_manifest_yaml(gameInstance: Path | str)->GameListEntry:
    """
    Read the manifest for a game, grabbing its 
    title and slug for display on the picker screen.
    """
    root = Path(gameInstance).resolve()
    manifest = root / "manifest.yaml"
    if manifest.exists():
        with manifest.open() as f:
            loaded = yaml.load(f)
        return GameListEntry(
            loaded.get("title", "A Game"), 
            loaded.get("slug", "Slug for a game"), 
            loaded.get("author", "Anonymous"),
            root)
    else:
        raise Exception("Not a valid game directory")

def scan_game_list(path:Path|str)->Iterator[GameListEntry]:
    """
    Scan a directory for game metadata.
    """
    pth = Path(path).resolve()
    for p in pth.iterdir():
        if p.is_dir() and (p / "manifest.yaml").exists():
            mfest = load_manifest_yaml(p)
            if mfest:
                yield mfest