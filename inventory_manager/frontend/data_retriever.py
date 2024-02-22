from googleapiclient.discovery import build
from google.auth.external_account_authorized_user import Credentials


def gen(creds: Credentials):
    with build("sheets", "v4", credentials=creds) as service:
        id = "19RL_OmUs_ODDRDpGcOKtCVufElH6EIyLb8fnQMTMhPc"
        sh = service.spreadsheets().values()
        print(
            sh.batchGet(
                spreadsheetId=id, ranges=["A1:B2"], majorDimension="ROWS"
            ).execute()
        )
