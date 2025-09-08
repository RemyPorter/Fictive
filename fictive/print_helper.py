import re
from .states import Statebag
from dataclasses import dataclass


@dataclass
class TemplateMatch:
    """
    Helper class for scanning for template strings.
    """
    start: int  # the start of the match
    end: int  # the end of the match
    key: str  # the key value inside the "{}"s


def scan_for_template(text: str) -> TemplateMatch | None:
    """
    Scan through a string for template entries. Supports escaping with \\.
    """
    escaped: bool = False
    templateStarted = False
    templateStartIdx: int = 0
    for i, c in enumerate(text):
        if escaped:
            escaped = False
            continue
        if c == "\\":
            escaped = True
        if c == "{" and not templateStarted:
            templateStarted = True
            templateStartIdx = i
        elif c == "}" and templateStarted:
            return TemplateMatch(
                templateStartIdx,
                i+1,
                text[templateStartIdx+1:i]
            )
    return None


def statify(text: str, statebag: Statebag):
    """
    Handles templating inside of state strings.

    Any `{someKey}` will be replaced by `someKey` from the statebag. If `somekey`
    does not exist, an error will be printed out instead.
    """
    match = scan_for_template(text)
    result = text  # our final output
    working = text  # our working copy that we truncate as we work
    while (match):
        to_replace = working[match.start: match.end]
        replace_with = statebag.get(
            match.key, f"<<ERROR: {match.key} not in state bag>>")
        # only replace one at a time, so our result and our working don't get out of sync
        result = result.replace(to_replace, str(replace_with), 1)
        working = working[match.end:]
        match = scan_for_template(working)
    return result
