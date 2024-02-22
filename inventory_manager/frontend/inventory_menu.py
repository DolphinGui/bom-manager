from io import TextIOWrapper
from pathlib import Path
from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.screen import Screen
from rich.text import Text
from rich.markup import escape
from google.auth.external_account_authorized_user import Credentials
from googleapiclient.discovery import build
from textual.message import Message
from textual.events import Key
from textual.coordinate import Coordinate


def notate_r1(coord: Coordinate) -> str:
    col = chr(ord("@") + 1 + coord.column)
    return col + str(coord.row + 2)


class InventoryMenu(Screen):
    BINDINGS = [("ctrl+s", "save", "Save changes"), ("ctrl+l", "load", "Load changes")]

    credentials: Credentials
    sheet_id: str
    changelist: set[Coordinate]
    file: TextIOWrapper

    def __init__(self, credentials: Credentials, sheet_id: str) -> None:
        self.credentials = credentials
        self.sheet_id = sheet_id
        self.file = Path("out.txt").open("a+")
        self.changelist = set[Coordinate]()
        self.file.write(str(self.changelist))
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield DataTable[str]()

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
        with build("sheets", "v4", credentials=self.credentials) as service:
            sh = service.spreadsheets()
            metadata = sh.get(
                spreadsheetId=self.sheet_id, includeGridData=True
            ).execute()
            rows = len(metadata["sheets"][0]["data"][0]["rowMetadata"])
            cols = len(metadata["sheets"][0]["data"][0]["columnMetadata"])
            self.post_message(
                self.SheetData(
                    sh.values()
                    .batchGet(
                        spreadsheetId=self.sheet_id,
                        ranges=[f"R[0]C[0]:R[{rows}]C[{cols}]"],
                        majorDimension="ROWS",
                    )
                    .execute()["valueRanges"][0]["values"]
                )
            )

    def action_save(self) -> None:
        table = self.query_one(DataTable[str])
        request = {
            "data": [
                {"range": notate_r1(x), "values": [[str(table.get_cell_at(x))]]}
                for x in self.changelist
            ],
            "valueInputOption": "USER_ENTERED",
        }
        with build("sheets", "v4", credentials=self.credentials) as service:
            sh = service.spreadsheets().values()
            sh.batchUpdate(spreadsheetId=self.sheet_id, body=request).execute()

    def on_key(self, event: Key) -> None:
        table = self.query_one(DataTable[str])
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
        table = self.query_one(DataTable[str])
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

    def on_mount(self) -> None:
        self.update_table()
