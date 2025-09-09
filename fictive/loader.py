from ruamel.yaml import YAML
from pathlib import Path
from contextlib import ExitStack
from typing import List, Iterator, Tuple

yaml=YAML(typ='safe')   # default,

def merge_game_yaml(root: Path, manifest: Path) -> Tuple[dict, str]:
    """
    By reading the manifest, load all the files in that manifest and
    merge them into a single string so we can parse it in YAML.
    """
    if manifest.exists():
        with manifest.open() as f:
            mfest = yaml.load(f)
            files = [root / entry for entry in mfest["files"]]
        with ExitStack() as stack:
            read_from = [stack.enter_context(
                entry.open()).read() for entry in files]
        merged = "\n".join(read_from)
        return mfest,merged
    return None

def load_game_yaml(gameInstance: Path | str):
    """
    Load a game from a directory, by scanning the `files` 
    entry in the manifest.
    """
    root = Path(gameInstance).resolve()
    if not root.is_dir():  # the game is in a single file
        with root.open() as f:
            return yaml.load(f)
    # otherwise, the game is in a directory, look for a manifest
    manifest = root / "manifest.yaml"
    mfest, merged = merge_game_yaml(root, manifest)
    if merged:
        loaded = yaml.load(merged)
        return loaded + [{key: value} for key, value in mfest.items()]
    return None


def load_manifest_yaml(gameInstance: Path | str):
    """
    Read the manifest for a game, grabbing its 
    title and slug for display on the picker screen.
    """
    root = Path(gameInstance).resolve()
    manifest = root / "manifest.yaml"
    if manifest.exists():
        with manifest.open() as f:
            loaded = yaml.load(f)
        return loaded.get("title", "A Game"), loaded.get("slug", "Slug for a game"), loaded.get("author", "Anonymous")
    return None