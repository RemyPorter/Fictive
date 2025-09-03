import re
from .states import Statebag

LABEL = re.compile(r"\{(.+?)\}")


def statify(text: str, statebag: Statebag):
    """
    Handles templating inside of state strings.

    Any `{someKey}` will be replaced by `someKey` from the statebag. If `somekey` 
    does not exist, an error will be printed out instead.
    """
    match = LABEL.search(text)
    while (match):
        to_replace = text[match.span()[0]:match.span()[1]]
        replace_with = statebag.get(
            match.groups()[0], f"<<ERROR: {to_replace[1:-1]} not in state bag>>")
        text = text.replace(to_replace, str(replace_with))
        match = LABEL.search(text)
    return text
