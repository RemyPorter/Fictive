import yaml
from pathlib import Path
from contextlib import ExitStack


def load_yaml(gameInstance: Path | str):
    root = Path(gameInstance).resolve()
    if not root.is_dir():  # the game is in a single file
        with root.open() as f:
            return yaml.load(f, yaml.SafeLoader)
    # otherwise, the game is in a directory, look for a manifest
    manifest = root / "manifest.yaml"
    with manifest.open() as f:
        files = [root / entry for entry in yaml.load(f, yaml.SafeLoader)]
    with ExitStack() as stack:
        read_from = [stack.enter_context(
            entry.open()).read() for entry in files]
    merged = "\n".join(read_from)

    return yaml.load(merged, yaml.SafeLoader)
