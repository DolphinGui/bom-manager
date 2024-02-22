from google_auth_oauthlib.flow import InstalledAppFlow
from appdirs import AppDirs
from google.auth.external_account_authorized_user import Credentials
from httplib2 import Http
import google_auth_httplib2
from textual.app import ComposeResult
from textual.widgets import Label, LoadingIndicator
from textual.screen import ModalScreen
import inventory_manager.cache as cache

app_dirs = AppDirs("Inventory Manager", "Shin Umeda", "1.0")
dir = app_dirs.user_config_dir


class AuthMenu(ModalScreen[Credentials]):
    def compose(self) -> ComposeResult:
        yield Label("Authenticating...")
        yield LoadingIndicator()

    def on_mount(self):
        creds = get_creds()
        if creds.expired:
            http = Http()
            creds.refresh(google_auth_httplib2.Request(http))
        self.dismiss(creds)


def get_creds() -> Credentials:
    x = cache.getFile("creds.json")
    flow = InstalledAppFlow.from_client_secrets_file(
        cache.loadFile("secrets.json"),
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ],
    )
    if not x.exists():
        creds = flow.run_local_server()
        file = x.open("w")
        # token is encoded as token_uri instead of token_url for some reason
        file.write(creds.to_json().replace("token_uri", "token_url"))
        return creds
    else:
        return Credentials.from_file(x)
