from textual import on
from textual.app import ComposeResult
from textual.widgets import ListView, Input, ListItem, Label
from textual.screen import ModalScreen
from typing import Optional

from inventory_manager.backend.sheets import AccessKey


class Sheet(ListItem):
    file: AccessKey.TableName

    def __init__(self, sheet: AccessKey.TableName) -> None:
        self.file = sheet
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.file.name)


class FileSelect(ModalScreen[str]):
    files: list[Sheet]
    credentials: AccessKey

    def __init__(self, creds: AccessKey) -> None:
        self.credentials = creds
        self.search()
        super().__init__()

    def search(self, term: Optional[str] = None) -> None:
        tables = self.credentials.list_tables(term)
        self.files = [Sheet(sheet=AccessKey.TableName(x.name, x.id)) for x in tables]

    @on(ListView.Selected)
    def choose(self, event: ListView.Selected) -> None:
        self.dismiss(event.item.file.id)  # type: ignore

    def compose(self) -> ComposeResult:
        yield Input(type="text")
        yield ListView(*self.files)

    @on(Input.Submitted)
    def submit_query(self, event: Input.Submitted) -> None:
        self.search(event.value)
        list = self.query_one(ListView)
        list.clear()
        for f in self.files:
            list.append(f)
