from textual.app import App
from inventory_manager.backend.base import AccessKey
from inventory_manager.backend.sheets import GoogleCreds
from .cache import getLogpath, loadFile
from .frontend.auth import AuthMenu
from .frontend.file_select import FileSelect
from .frontend.inventory_menu import InventoryMenu
from textual import work
from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header
from textual.containers import Center
from textual import on
import json as json
from weakref import finalize
import logging
from .frontend.loading_screen import LoadingScreen


def entry():
    app = ManagerApp()
    app.run()


class ManagerApp(App):
    def __init__(self):
        super().__init__()
        logging.basicConfig(
            filename=getLogpath(), encoding="utf-8", level=logging.DEBUG
        )

    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
    ]
    CSS_PATH = "app.tcss"
    SCREENS = {}

    credentials: AccessKey
    config: dict

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Center():
            yield Button("Inventory Management", id="inv")
            yield Button("BOM Management", id="bom")
            yield Button("Buy items", id="buy")

    @work
    @on(Button.Pressed, "#inv")
    async def action_inv(self):
        if "inv_id" not in self.config.keys():
            self.config.update(
                {"inv_id": await self.push_screen_wait(FileSelect(self.credentials))}
            )
        self.push_screen(InventoryMenu(self.config["inv_id"]))

    @work
    @on(Button.Pressed, "#bom")
    async def action_bom(self):
        if "bom_id" not in self.config.keys():
            self.config.update(
                {"bom_id": await self.push_screen_wait(FileSelect(self.credentials))}
            )
        self.push_screen(InventoryMenu(self.config["bom_id"]))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_loading_screen(self, message: str) -> None:
        self.push_screen(LoadingScreen(message))

    @work
    async def on_mount(self):
        self.title = "Inventory Manager"
        cached = GoogleCreds.cached()
        if not cached:
            self.push_screen(AuthMenu())
        self.credentials = GoogleCreds()
        if not cached:
            self.pop_screen()

        self.config = json.loads(loadFile("config.json").read_text())

        def write_config(self):
            f = loadFile("config.json")
            f.write_text(json.dumps(self.config))

        finalize(self, write_config, self)
