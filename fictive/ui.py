import curses as cu
import curses.textpad as textpad
from dataclasses import dataclass
from .states import Machine, Statebag, State
from .print_helper import statify, wrap_text
from textwrap import wrap

@dataclass
class WindowHolder:
    mainState: cu.window
    subState: cu.window
    transients: cu.window
    prompt: cu.window

MAIN_HEIGHT=12
SUB_HEIGHT=10
TRANS_HEIGHT=4
PROMPT_HEIGHT=3

class UI:
    def __init__(self, width:int=80):
        self._width = width
        self._windows = WindowHolder(
            cu.newwin(MAIN_HEIGHT,width,0,0),
            cu.newwin(SUB_HEIGHT,width,MAIN_HEIGHT,0),
            cu.newwin(TRANS_HEIGHT,width,MAIN_HEIGHT+SUB_HEIGHT,0),
            cu.newwin(PROMPT_HEIGHT,width,MAIN_HEIGHT+SUB_HEIGHT+TRANS_HEIGHT,0)
        )
        self._inp = ""

    def update_state(self, s:State, b:Statebag):
        ms = self._windows.mainState
        lines = wrap_text(s.description(), self._width-2)
        ms.resize(len(lines)+3,self._width)
        ms.erase()
        ms.box()
        if "main.title" in b:
            ms.addstr(0,1,b["main.title"])
        for i,line in enumerate(lines):
            ms.addstr(1+i,1,line)
        ms.refresh()

    def update_substates(self, s:State, b:Statebag):
        ss = self._windows.subState
        subs = s.substates()
        ss.erase()
        if len(subs) > 0:
            joined = "\n".join(subs)
            wrapped = wrap_text(joined, self._width-2)
            ss.resize(len(wrapped)+3,self._width)
            ss.mvwin(self._windows.mainState.getmaxyx()[0], 0)
            ss.box()
            if "sub.title" in b:
                ss.addstr(0,1,b["sub.title"])
            for i,line in enumerate(wrapped):
                ss.addstr(1+i,1,line)
            ss.refresh()

    def update_transients(self, s:State, b:Statebag):
        pass

    def read_text(self, pm):
        key = pm.getkey()
        acc = ""
        while key != "\n":
            acc += key
            pm.addstr(1, 1, "> " + acc)
            key = pm.getkey()
        return acc


    def update_textbox(self):
        pm = self._windows.prompt
        y = self._windows.mainState.getmaxyx()[0] + \
            self._windows.subState.getmaxyx()[0]
        pm.erase()
        pm.mvwin(y,0)
        pm.box()
        pm.addstr(1, 1, "> ")
        pm.move(1, 4)
        pm.refresh()
        return self.read_text(pm)
        

    def update(self, s:State, b:Statebag):
        self.update_state(s, b)
        self.update_substates(s, b)
        return self.update_textbox()

