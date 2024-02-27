from textual.app import App
from inventory_manager.backend.base import AccessKey
from inventory_manager.backend.sheets import GoogleCreds
from .cache import getLogpath, loadFile
from .frontend.auth import AuthMenu
from .frontend.file_select import FileSelect
from textual.screen import Screen
from .frontend.inventory_menu import InventoryMenu
from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header
from textual.containers import Center
import json as json
from weakref import finalize
import logging
from .frontend.loading_screen import LoadingScreen


def entry():
    app = ManagerApp()
    app.run()


class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Center():
            yield Button("Inventory Management", id="inv")
            yield Button("BOM Management", id="bom")
            yield Button("Buy items", id="buy")

    @work(thread=True)
    async def on_mount(self):
        self.title = "Inventory Manager"


class ManagerApp(App):
    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
        ("d", "switch_mode('dash')", "Dashboard"),
        ("b", "switch_mode('bom')", "BOM"),
        ("i", "switch_mode('inv')", "Inventory"),
    ]

    config: dict[str, str] = {}
    SCREENS = {
        "dash": MainMenu(),
        "bom": InventoryMenu("bom_id", config),
        "inv": InventoryMenu("inv_id", config),
    }
    MODES = {
        "dash": "dash",
        "bom": "bom",
        "inv": "inv",
    }

    CSS_PATH = "app.tcss"
    credentials: AccessKey

    @work(thread=True)
    async def get_credentials(self):
        self.credentials = GoogleCreds()
        self.pop_screen()
        pass

    def __init__(self):
        super().__init__()
        logging.basicConfig(
            filename=getLogpath(), encoding="utf-8", level=logging.DEBUG
        )

        self.config = json.loads(loadFile("config.json").read_text())

        def write_config(self):
            f = loadFile("config.json")
            f.write_text(json.dumps(self.config))

        finalize(self, write_config, self)

    def on_mount(self):
        self.switch_mode("dash")
        cached = GoogleCreds.cached()
        if not cached:
            self.push_screen(AuthMenu())
            self.call_after_refresh(self.get_credentials)
        else:
            self.credentials = GoogleCreds()

    @on(Button.Pressed, "#inv,#bom")
    def change_mode(self, event: Button.Pressed) -> None:
        self.switch_mode(str(event.button.id))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_loading_screen(self, message: str) -> None:
        self.push_screen(LoadingScreen(message))
