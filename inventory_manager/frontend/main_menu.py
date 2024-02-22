from textual.app import ComposeResult
from textual.widgets import Button, Footer, Header
from textual.screen import Screen
from textual import on


class MainMenu(Screen):
    BINDINGS = [("i", "inv", "Manage Inventory"), ("b", "bom", "Manage BOM")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Button("Inventory Management", id="inv")
        yield Button("BOM Management", id="bom")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
    
    @on(Button.Pressed, "#inv")
    def action_inv(self):
        self.push_screen("inv")
