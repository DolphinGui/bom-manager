from textual.app import ComposeResult
from textual.widgets import Label, LoadingIndicator
from textual.screen import ModalScreen


class AuthMenu(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Label("Authenticating...")
        yield LoadingIndicator()
