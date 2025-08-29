import curses as cu
import curses.textpad as textpad
from dataclasses import dataclass
from .states import Machine, Statebag, State
from .print_helper import statify, wrap_text
from textwrap import wrap
from typing import Tuple
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, Input
from textual.containers import Vertical
from textual import on


class FictiveUI(App):
    game: Machine = None
    state_bag: Statebag = None
    started: bool = False

    CSS_PATH = "fictive.tcss"

    def on_mount(self) -> None:
        self.update(None, self.game.current())
        self._started = True

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Markdown(id="State", open_links=False),
            Markdown(id="Substate", open_links=False),
            Markdown(id="Transients", open_links=False)
        )
        yield Input(placeholder="Enter a command")
        yield Footer()

    def update(self, t: Machine.Result, s: State, transients: State = None):
        if t == Machine.Result.End:
            # do something here!
            pass
        self.query_exactly_one("#State").update(
            statify(s.description(), self.state_bag)
        )
        subs = self.query_exactly_one("#Substate")
        trans = self.query_exactly_one("#Transients")
        if len(s.substates()) > 0:
            subs.update(statify("\n\n".join(s.substates()), self.state_bag))
            subs.classes = "active"
        else:
            subs.classes = "inactive"
        if transients:
            trans.classes = "active"
        else:
            trans.classes = "inactive"

        self.query_exactly_one("#Substate").update("\n".join(s.substates()))

    @on(Input.Submitted)
    def input(self, event: Input.Changed) -> None:
        inp = event.value
        t, s = self.game.step(inp, self.state_bag)
        self.update(t, s)
        self.query_one(Input).value = ""


@dataclass
class WindowHolder:
    mainState: cu.window
    subState: cu.window
    transients: cu.window
    prompt: cu.window


MAIN_HEIGHT = 12
SUB_HEIGHT = 10
TRANS_HEIGHT = 4
PROMPT_HEIGHT = 3


class TextBox:
    def __init__(self, parent: cu.window, offset: Tuple[int, int]):
        y, x = offset
        self._parent = parent
        h, w = parent.getmaxyx()
        self._win = parent.derwin(1, w-5, y, x)
        self._offset = offset

    def edit(self):
        pm = self._win
        pm.move(0, 0)
        key = pm.get_wch()
        acc = ""
        while key != "\n":
            if ord(key) in (cu.KEY_BACKSPACE, 127, 263) and len(acc) > 0:
                acc = acc[0:-1]
            else:
                acc += key
            pm.erase()
            pm.addstr(acc)
            pm.refresh()
            key = pm.get_wch()
        return acc
