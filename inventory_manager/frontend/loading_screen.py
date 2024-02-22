from textual.app import ComposeResult
from textual.widgets import Label, LoadingIndicator
from textual.screen import ModalScreen


class LoadingScreen(ModalScreen):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.message)
        yield LoadingIndicator()

    def action_end_loading(self):
        self.dismiss()
