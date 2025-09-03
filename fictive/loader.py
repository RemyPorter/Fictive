import yaml
from pathlib import Path
from contextlib import ExitStack


def load_game_yaml(gameInstance: Path | str):
    """
    Load a game from a directory, by scanning the `files` 
    entry in the manifest.
    """
    root = Path(gameInstance).resolve()
    if not root.is_dir():  # the game is in a single file
        with root.open() as f:
            return yaml.load(f, yaml.SafeLoader)
    # otherwise, the game is in a directory, look for a manifest
    manifest = root / "manifest.yaml"
    with manifest.open() as f:
        mfest = yaml.load(f, yaml.SafeLoader)
        files = [root / entry for entry in mfest["files"]]
    with ExitStack() as stack:
        read_from = [stack.enter_context(
            entry.open()).read() for entry in files]
    merged = "\n".join(read_from)

    loaded = yaml.load(merged, yaml.SafeLoader)
    return loaded + [{key: value} for key, value in mfest.items()]


def load_manifest_yaml(gameInstance: Path | str):
    """
    Read the manifest for a game, grabbing its 
    title and slug for display on the picker screen.
    """
    root = Path(gameInstance).resolve()
    manifest = root / "manifest.yaml"
    with manifest.open() as f:
        loaded = yaml.load(f, yaml.SafeLoader)
    return loaded.get("title", "A Game"), loaded.get("slug", "Slug for a game"), loaded.get("author", "Anonymous")
