import json
from .base import Table, AccessKey, Update
from google.auth.external_account_authorized_user import Credentials as ExCred
from google.oauth2.credentials import Credentials as OathCred
from .. import cache
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import Request
from httplib2 import Http
from googleapiclient.discovery import build
from ..secrets import secretjson

Credentials = ExCred | OathCred


def notate_r1(row: int, column: int) -> str:
    col = chr(ord("@") + column + 1)
    return col + str(row + 1)


def notate_r1r1(cbegin: int, rbegin: int, cend: int, rend: int) -> str:
    return notate_r1(cbegin, rbegin) + ":" + notate_r1(cend - 1, rend - 1)


class GoogleSheets(Table):
    credentials: Credentials
    sheet_id: str

    def __init__(self, credentials: Credentials, sheet_id: str) -> None:
        self.credentials = credentials
        self.sheet_id = sheet_id

    def get_data(self, sheet: str) -> list[list[str]]:
        with build("sheets", "v4", credentials=self.credentials) as service:
            sh = service.spreadsheets()
            metadata = sh.get(
                spreadsheetId=self.sheet_id, includeGridData=True
            ).execute()
            rows = len(metadata["sheets"][0]["data"][0]["rowMetadata"])
            cols = len(metadata["sheets"][0]["data"][0]["columnMetadata"])
            return (
                sh.values()
                .batchGet(
                    spreadsheetId=self.sheet_id,
                    ranges=[f"R[0]C[0]:R[{rows}]C[{cols}]"],
                    majorDimension="ROWS",
                )
                .execute()["valueRanges"][0]["values"]
            )

    def list_sheets(self) -> list[str]:
        raise NotImplementedError()

    def update(self, sheet: str, updates: list[Update]) -> None:
        request = {
            "data": [
                {"range": notate_r1(x.location[0], x.location[1]), "values": [[x.data]]}
                for x in updates
            ],
            "valueInputOption": "USER_ENTERED",
        }
        with build("sheets", "v4", credentials=self.credentials) as service:
            sh = service.spreadsheets().values()
            sh.batchUpdate(spreadsheetId=self.sheet_id, body=request).execute()

    def full_update(self, sheet: str, data: list[list[str]]) -> None:
        r_len = len(data)
        c_len = len(max(data, key=len))
        request = {
            "data": [{"range": notate_r1r1(0, 0, r_len, c_len), "values": data}],
            "valueInputOption": "USER_ENTERED",
        }
        with build("sheets", "v4", credentials=self.credentials) as service:
            sh = service.spreadsheets().values()
            sh.batchUpdate(spreadsheetId=self.sheet_id, body=request).execute()


Table.register(GoogleSheets)


class GoogleCreds(AccessKey):
    credentials: Credentials

    def __init__(self):
        x = cache.getFile("creds.json")
        if not x.exists():
            flow = InstalledAppFlow.from_client_config(
                json.loads(secretjson),
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.metadata.readonly",
                ],
            )
            creds = flow.run_local_server()
            file = x.open("w")
            # token is encoded as token_uri instead of token_url for some reason
            file.write(creds.to_json().replace("token_uri", "token_url"))
            self.credentials = creds
        else:
            self.credentials = ExCred.from_file(x)
        if self.credentials.expired:
            http = Http()
            self.credentials.refresh(Request(http))

    @staticmethod
    def cached() -> bool:
        x = cache.getFile("creds.json")
        return x.exists()

    def list_tables(self, term: str | None) -> list[AccessKey.TableName]:
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
            return [AccessKey.TableName(x["name"], x["id"]) for x in sh["files"]]

    def get_table(self, id: str) -> GoogleSheets:
        return GoogleSheets(self.credentials, id)


AccessKey.register(GoogleCreds)
