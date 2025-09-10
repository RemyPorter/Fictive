"""
Our UI classes, which lets people actually play the game.
"""
from enum import StrEnum
from .states import Machine, Statebag, State
from .print_helper import statify
from .parser import *
from .loader import load_game_yaml, scan_game_list
from .game_server import get_game_server
from textwrap import wrap
from typing import Tuple, Iterable
from pathlib import Path
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.message import Message
from textual.widgets import Footer, Header, Markdown, Input, Label, ListView, ListItem, DataTable, Static, Pretty
from textual.containers import Vertical, Container, Horizontal, VerticalScroll
from textual import on
from textual.command import Hit, Hits, Provider


class StatebagPeek(Widget):
    """
    Helper to show our statebag, for debugging
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Pretty(get_game_server().bag())

    def update(self):
        self.query_exactly_one("Pretty").update(get_game_server().bag())


class DisplayWrapper(Widget):
    """
    Simple container for our Markdown widget, which will actually
    be what displays game state
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Markdown()

    def update(self, body: str, title: str | None):
        self.border_title = title
        self.query_exactly_one(Markdown).update(body)
        pass


class GameUI(Screen):
    """
    A screen for playing the game.
    """
    class GameOver(Message):
        """
        An event for ending the game
        """
        pass

    class Banners(StrEnum):
        """Helper enum for managing banners"""
        state = "state"
        sub = "sub"
        trans = "trans"

    BINDINGS = {
        Binding("ctrl+x", "quit_game", "Quit the Game", show=True)
    }

    def action_quit_game(self):
        """
        Callback for our binding (doesn't currently work)
        """
        self.quit_game()

    def quit_game(self):
        """
        Emit an event notifying our controller to quit the game.
        """
        self.post_message(GameUI.GameOver())

    def __init__(self, *args, **kwargs):
        self.ended = False
        self._peek = False
        super().__init__(*args, **kwargs)

    def show_statebag(self):
        peeker = self.query_exactly_one("#Peek")
        if self._peek:
            peeker.classes = "inactive"
        else:
            peeker.classes = "active"
        self._peek = not self._peek

    def on_mount(self) -> None:
        # properly init our view without ticking the game forward
        self.update(Machine.StepResult(None, get_game_server().current(),None), get_game_server().bag())
        self.focus_next(Input)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical():
                yield DisplayWrapper(id="State")
                yield DisplayWrapper(id="Substate")
                yield DisplayWrapper(id="Transient", classes="inactive")
                yield DisplayWrapper(id="Error", classes="inactive")
            yield StatebagPeek(id="Peek", classes="inactive")
        yield Input(placeholder="Enter a command…")
        yield Footer()

    def get_banner(self, level: "GameUI.Banners", state_bag:Statebag) -> str:
        return statify(state_bag.get(str(level) + ".banner", ""), state_bag)

    def display_error(self, err:str):
        err = self.query_exactly_one("#Error")
        err.classes = "active"
        err.update(res.additionalMessages, "ERROR")

    def clear_error(self):
        self.query_exactly_one("#Error").classes = "inactive"

    def update_state(self, tick:Machine.StepResult, state_bag:Statebag):
        state_banner = self.get_banner(GameUI.Banners.state, state_bag)
        # Update the main state box
        self.query_exactly_one("#State").update(
            statify(tick.state.description(), state_bag), state_banner
        )

    def update_substate(self, tick:Machine.StepResult, state_bag:Statebag):
        subs_banner = self.get_banner(GameUI.Banners.sub, state_bag)
        # update the substate box
        subs = self.query_exactly_one("#Substate")
        if len(tick.state.substates()) > 0:
            subs.update(statify("\n\n".join(tick.state.substates()),
                        state_bag), subs_banner)
            subs.classes = "active"
        else:
            subs.classes = "inactive"

    def update_transients(self, tick:Machine.StepResult, state_bag:Statebag):
        trans_banner = self.get_banner(GameUI.Banners.trans, state_bag)
        # update the transient state box
        trans = self.query_exactly_one("#Transient")
        if tick.transient:
            trans.classes = "active"
            trans.update(statify(tick.transient.description(),
                         state_bag), trans_banner)
        else:
            trans.classes = "inactive"

    def update(self, tick:Machine.StepResult, state_bag:Statebag):
        """
        Update the UI based on the last game tick.
        """
        if tick.action == Machine.Result.End:
            self.ended = True
        if tick.action == Machine.Result.Error:
            self.display_error(tick.additionalMessages)
        else:
            self.clear_error()
        
        self.update_state(tick, state_bag)
        self.update_substate(tick, state_bag)
        self.update_transients(tick, state_bag)
        # update our debugging view
        self.query_exactly_one("#Peek").update()

    @on(Input.Submitted)
    def input(self, event: Input.Changed) -> None:
        """
        Handle user input in our text box. If the game has ended, the
        next time we hit enter, it dumps us back to the game picker screen
        """
        if self.ended:
            self.quit_game()
            return
        inp = event.value
        res, state_bag = get_game_server().tick(inp)
        self.update(res, state_bag)
        self.query_one(Input).value = ""


class GameList(Widget):
    """
    A widget showing all of our games.
    """
    class GamePicked(Message):
        """
        Event for when the user has picked a game.
        """

        def __init__(self, path):
            self.path = path
            super().__init__()

    games: Iterable[ListItem] = []

    def __init__(self, path):
        super().__init__()
        self.path = path

    def on_mount(self):
        dt = self.query_exactly_one(DataTable)
        dt.add_column("Game")
        dt.add_column("Description")
        dt.add_column("Author")
        self.display()

    def display(self):
        dt = self.query_exactly_one(DataTable)
        self.games = [g for g in scan_game_list(self.path)]
        dt.clear()
        for g in self.games:
            dt.add_row(g.title, g.slug, g.author)

    def on_screen_resume(self):
        self.display()

    def compose(self):
        yield DataTable(zebra_stripes=True, cursor_type="row")

    @on(DataTable.RowSelected)
    def on_selected(self, item: DataTable.RowSelected):
        idx = item.cursor_row
        self.post_message(
            GameList.GamePicked(
                self.games[idx].path)
        )


class GamePicker(Screen):
    """
    The introduction screen for picking games
    """

    def __init__(self, path, *args, **kwargs):
        self.path = Path(path)
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Header()
        yield Static("""
 _______ _             _             
(_______|_)        _  (_)            
 _____   _  ____ _| |_ _ _   _ _____ 
|  ___) | |/ ___|_   _) | | | | ___ |
| |     | ( (___  | |_| |\ V /| ____|
|_|     |_|\____)  \__)_| \_/ |_____)
        """, id="banner")
        yield Markdown("""
 Pick a game you'd like to play.        
        """)
        yield GameList(self.path)
        yield Footer()


class FictiveUI(App):
    TITLE = "Fictive Game Player"

    CSS_PATH = "fictive.tcss"

    def __init__(self, path, *args, debug: bool = False, **kwargs):
        self.path = path
        self.debug_enabled = debug

        super().__init__(*args, **kwargs)

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        if isinstance(screen, GameUI):
            yield SystemCommand("Exit Game", "Return to the main menu", screen.quit_game)
            if self.debug_enabled:
                yield SystemCommand("Peek Statebag", "Show the statebag", screen.show_statebag)

    def on_mount(self):
        self.title = FictiveUI.TITLE
        self.install_screen(GamePicker(path=self.path), name="picker")
        self.push_screen("picker")

    @on(GameList.GamePicked)
    def on_game_picked(self, picked: GameList.GamePicked):
        loaded = load_game_yaml(Path(picked.path))
        if not loaded:
            # this game didn't have a manifest
            # this shouldn't happen
            return # TODO: handle error
        game, state_bag, title = parse(loaded)
        get_game_server().start(game, state_bag)
        gameUI = GameUI()
        self.install_screen(gameUI, name="running_game")
        self.push_screen("running_game")
        self.title = title

    @on(GameUI.GameOver)
    def on_game_over(self, go: GameUI.GameOver):
        self.pop_screen()
        self.uninstall_screen("running_game")
        self.title = FictiveUI.TITLE
