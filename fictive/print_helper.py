import re
from .states import Statebag
from typing import Iterable
from textwrap import wrap

def print_line(line:str, w:int=80):
    """
    Print a line, automatically breaking at the space nearest to
    `w` characters wide. This is to fit neatly into terminals.
    """
    length = len(line)
    if length <= w: # string is shorter than our window
        print(line)
        return
    n = 0
    while n < length:
        if n+w > length: # the last block of the string
            print(line[n:])
            return
        window = line[n:n+w]
        split_at = window.rfind(" ")
        if split_at >= 0:
            print(window[0:split_at])
            n += split_at + 1
        else:
            print(window[0:w])
            n += w
        
def margined_print(text:str, w:int=80):
    """
    Print a multiline block of text across multiple wrapped lines,
    wrapping at `w` characters wide
    """
    lines = text.split("\n")
    for l in lines:
        print_line(l, w)

LABEL=re.compile(r"\{(.+?)\}")

def statify(text:str, statebag:Statebag):
    match = LABEL.search(text)
    while(match):
        to_replace = text[match.span()[0]:match.span()[1]]
        replace_with = statebag[match.groups()[0]]
        text = text.replace(to_replace, str(replace_with))
        match = LABEL.search(text)
    return text

def print_sections(sections:Iterable[str], statebag:Statebag, width:int, separator:str="━"):
    print("\033c", "")
    for section in sections:
        s = statify(section, statebag)
        margined_print(s, width)
        print(separator * width)

def wrap_text(text:str, width:int=80)->Iterable[str]:
    lines = wrap(text, replace_whitespace=False, drop_whitespace=True)
    res = []
    for l in lines:
        s = l.split("\n")
        res += s
    return res