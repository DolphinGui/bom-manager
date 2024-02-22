from google.auth.external_account_authorized_user import Credentials
from textual import on
from textual.app import ComposeResult
from textual.widgets import ListView, Input, ListItem, Label
from textual.screen import ModalScreen
from googleapiclient.discovery import build
from typing import NamedTuple, Optional


class SheetFile(NamedTuple):
    name: str
    id: str


class Sheet(ListItem):
    file: SheetFile

    def __init__(self, sheet: SheetFile) -> None:
        self.file = sheet
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.file.name)


class FileSelect(ModalScreen[str]):

    files: list[Sheet]
    credentials: Credentials

    def __init__(self, creds: Credentials) -> None:
        self.credentials = creds
        self.search()
        super().__init__()

    def search(self, term: Optional[str] = None) -> None:
        with build("drive", "v3", credentials=self.credentials) as service:
            if term is None:
                query = ""
            else:
                query = f"and name contains '{term}'"
            sh = (
                service.files()
                .list(
                    q="trashed=false and mimeType='application/vnd.google-apps.spreadsheet'"
                    + query
                )
                .execute()
            )
            self.files = [
                Sheet(sheet=SheetFile(x["name"], x["id"])) for x in sh["files"]
            ]

    @on(ListView.Selected)
    def choose(self, event: ListView.Selected)-> None:
        self.dismiss(event.item.file.id)


    def compose(self) -> ComposeResult:
        yield Input(type="text")
        yield ListView(*self.files)

    @on(Input.Submitted)
    def show_invalid_reasons(self, event: Input.Submitted) -> None:
        self.search(event.value)
        list = self.query_one(ListView)
        list.clear()
        for f in self.files:
            list.append(f)

