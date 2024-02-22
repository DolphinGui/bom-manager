from pathlib import Path
from google.auth.external_account_authorized_user import Credentials
from typing import Optional
from textual.app import App
from inventory_manager.frontend.auth import AuthMenu
from inventory_manager.frontend.file_select import FileSelect
from inventory_manager.frontend.inventory_menu import InventoryMenu
from textual import work
from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header
from textual.containers import Center
from textual import on

from inventory_manager.frontend.loading_screen import LoadingScreen


def entry():
    app = ManagerApp()
    app.run()


class ManagerApp(App):
    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
    ]
    CSS_PATH = "app.tcss"
    SCREENS = {}

    credentials: Optional[Credentials]

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
        id = await self.push_screen_wait(FileSelect(self.credentials))
        self.push_screen(InventoryMenu(self.credentials, id))

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_loading_screen(self, message: str) -> None:
        self.push_screen(LoadingScreen(message))

    @work
    async def on_mount(self):
        self.title = "Inventory Manager"
        self.credentials = await self.push_screen_wait(
            AuthMenu(),
        )
