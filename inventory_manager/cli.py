from textual.app import App
from inventory_manager.backend.base import AccessKey
from .backend.factories import get_key, cached
from .cache import getLogpath
from .frontend.auth import AuthMenu
from textual.screen import Screen
from .frontend.inventory_menu import InventoryMenu
from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header
from textual.containers import Center
import json as json
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
        ("ctrl+d", "switch_mode('dash')", "Dashboard"),
        ("ctrl+b", "switch_mode('bom')", "BOM"),
        ("ctrl+i", "switch_mode('inv')", "Inventory"),
    ]

    SCREENS = {
        "dash": MainMenu(),
        "bom": InventoryMenu("bom_id"),
        "inv": InventoryMenu("inv_id"),
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
        self.credentials = get_key()
        self.pop_screen()
        pass

    def __init__(self):
        super().__init__()
        logging.basicConfig(
            filename=getLogpath(), encoding="utf-8", level=logging.DEBUG
        )

    def on_mount(self):
        self.switch_mode("dash")
        if not cached():
            self.push_screen(AuthMenu())
            self.call_after_refresh(self.get_credentials)
        else:
            self.credentials = get_key()

    @on(Button.Pressed, "#inv,#bom")
    def change_mode(self, event: Button.Pressed) -> None:
        self.switch_mode(str(event.button.id))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_loading_screen(self, message: str) -> None:
        self.push_screen(LoadingScreen(message))
