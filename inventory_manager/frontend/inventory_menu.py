import logging
from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.screen import Screen
from rich.text import Text
from rich.markup import escape
from textual.message import Message
from textual.events import Key
from textual.coordinate import Coordinate

from inventory_manager.backend.base import Update
from inventory_manager.frontend.file_select import FileSelect
from ..backend.sheets import GoogleCreds, GoogleSheets
from ..cache import gconfig


class InventoryMenu(Screen):
    BINDINGS = [("ctrl+s", "save", "Save changes"), ("ctrl+l", "load", "Load changes")]

    changelist: set[Coordinate]
    creds: GoogleCreds
    sheets: GoogleSheets
    type: str

    def __init__(self, type: str) -> None:
        self.changelist = set[Coordinate]()
        self.type = type
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield DataTable[Text]()

    class SheetData(Message):
        data: list[list[str]]

        def __init__(self, data: list[list[str]]) -> None:
            self.data = data
            super().__init__()
            self.stop()

    def action_load(self) -> None:
        self.update_table()

    @work(exclusive=True, thread=True)
    async def update_table(self) -> None:
        self.post_message(self.SheetData(self.sheets.get_data("")))

    def action_save(self) -> None:
        table = self.query_one(DataTable[Text])
        self.sheets.update(
            "",
            [
                Update((x.row + 1, x.column), str(table.get_cell_at(x)))
                for x in self.changelist
            ],
        )

    def on_key(self, event: Key) -> None:
        table = self.query_one(DataTable[Text])
        coord = table.cursor_coordinate
        cell = table.get_cell_at(coord)
        if event.key == "backspace":
            cell = cell[:-1]
        elif not event.is_printable:
            return
        else:
            cell += event.character
        table.update_cell_at(coord, cell, update_width=True)
        table.refresh_coordinate(coord)
        self.changelist.update([coord])

    @on(SheetData)
    def handle_update(self, event: SheetData):
        table = self.query_one(DataTable[Text])
        table.clear()
        table.columns.clear()
        try:
            table.add_columns(*event.data[0])
            for row in event.data[1:]:
                styled_row = [
                    Text(escape(str(cell)), style="italic #03AC13", justify="right")
                    for cell in row
                ]
                table.add_row(*styled_row)
        except Exception as e:
            raise NameError from e

    @work
    async def on_mount(self) -> None:
        self.creds = GoogleCreds()
        if self.type not in gconfig:
            gconfig[self.type] = await self.app.push_screen_wait(FileSelect(self.creds))
        self.sheets = self.creds.get_table(gconfig[self.type])
        self.update_table()
