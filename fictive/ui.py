"""
Our UI classes, which lets people actually play the game.
"""
from .states import Machine, Statebag, State
from .print_helper import statify, wrap_text
from .parser import *
from .loader import load_game_yaml, load_manifest_yaml
from textwrap import wrap
from typing import Tuple, Iterable
from pathlib import Path
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.message import Message
from textual.widgets import Footer, Header, Markdown, Input, Label, ListView, ListItem, DataTable, Static
from textual.containers import Vertical, Container
from textual import on
from textual.command import Hit, Hits, Provider


class DisplayWrapper(Widget):
    """
    Simple container for our Markdown widget, which will actually
    be what displays game state
    """
    def compose(self) -> ComposeResult:
        yield Markdown(open_links=False)
        
    def update(self, body:str, title:str|None):
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

    def __init__(self, game:Machine, state_bag: Statebag, *args, **kwargs):
        self.game = game
        self.state_bag = state_bag
        self.ended = False
        game.start(state_bag)
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        # properly init our view without ticking the game forward
        self.update(None, self.game.current())

    def compose(self) -> ComposeResult:
        yield Header()
        yield DisplayWrapper(id="State")
        yield DisplayWrapper(id="Substate")
        yield DisplayWrapper(id="Transient", classes="inactive")
        yield Input(placeholder="Enter a command…")
        yield Footer()

    def update(self, t: Machine.Result, s: State, transients: State = None):
        """
        Our core UI loop. Checks what we got out of the state machine, and
        updates several UI elements.

        This includes:
        * The banner on our main state widget
        * The main state widget itself
        * The banner on our substate widget (if active)
        * The substate widget itself
        * Ditto, but for the transient box
        """
        if t == Machine.Result.End:
            self.ended = True
        state_banner = statify(self.state_bag.get("state.banner", ""), self.state_bag)
        subs_banner = statify(self.state_bag.get("sub.banner", ""), self.state_bag)
        trans_banner = statify(self.state_bag.get("trans.banner", ""), self.state_bag)
        self.query_exactly_one("#State").update(
            statify(s.description(), self.state_bag), state_banner
        )
        subs = self.query_exactly_one("#Substate")
        trans = self.query_exactly_one("#Transient")
        if len(s.substates()) > 0:
            subs.update(statify("\n\n".join(s.substates()), self.state_bag), subs_banner)
            subs.classes = "active"
        else:
            subs.classes = "inactive"
        if transients:
            trans.classes = "active"
            trans.update(statify(transients.description(), self.state_bag), trans_banner)
        else:
            trans.classes = "inactive"

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
        res = self.game.step(inp, self.state_bag)
        self.update(res.action, res.state, res.transient)
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

    games:Iterable[ListItem]=[]

    def __init__(self, path):
        super().__init__()
        self.paths = []
        path = Path(path)
        for p in path.iterdir():
            if p.is_dir():
                title_slug = load_manifest_yaml(p)
                self.games.append(title_slug)
                self.paths.append(p)
        self.path = path

    def on_mount(self):
        dt = self.query_exactly_one(DataTable)
        dt.add_column("Game")
        dt.add_column("Description")
        for title,slug in self.games:
            dt.add_row(title,slug)
        
    def compose(self):
        yield DataTable(zebra_stripes=True, cursor_type="row")

    @on(DataTable.RowSelected)
    def on_selected(self, item:DataTable.RowSelected):
        idx = item.cursor_row
        self.post_message(GameList.GamePicked(self.paths[idx]))

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
    game:Machine
    state_bag:Statebag

    TITLE="Fictive Game Player"

    CSS_PATH = "fictive.tcss"

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        if isinstance(screen, GameUI):
            yield SystemCommand("Exit Game", "Return to the main menu", screen.quit_game)

    def on_mount(self):
        self.title = FictiveUI.TITLE
        self.install_screen(GamePicker(path="./games"), name="picker")
        self.push_screen("picker")

    @on(GameList.GamePicked)
    def on_game_picked(self, picked:GameList.GamePicked):
        loaded = load_game_yaml(Path(picked.path))
        game, state_bag, title = parse(loaded)
        gameUI = GameUI(game, state_bag)
        self.install_screen(gameUI, name="running_game")
        self.push_screen("running_game")
        self.title = title

    @on(GameUI.GameOver)
    def on_game_over(self, go:GameUI.GameOver):
        self.pop_screen()
        self.uninstall_screen("running_game")
        self.title = FictiveUI.TITLE