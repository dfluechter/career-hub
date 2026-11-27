import base64
from pathlib import Path
from typing import Iterator

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailProvider:
    def __init__(
        self,
        *,
        credentials_path: Path,
        token_path: Path,
    ):
        self.credentials_path = credentials_path
        self.token_path = token_path

    def authenticate(self):
        credentials = None

        if self.token_path.exists():
            credentials = (
                Credentials.from_authorized_user_file(
                    str(self.token_path),
                    SCOPES,
                )
            )

        if (
            not credentials
            or not credentials.valid
        ):
            if (
                credentials
                and credentials.expired
                and credentials.refresh_token
            ):
                credentials.refresh(
                    Request()
                )

            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        "Gmail OAuth credentials nicht gefunden: "
                        f"{self.credentials_path}"
                    )

                flow = (
                    InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path),
                        SCOPES,
                    )
                )

                credentials = flow.run_local_server(
                    port=0,
                )

            self.token_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.token_path.write_text(
                credentials.to_json(),
                encoding="utf-8",
            )

        return credentials

    def build_service(self):
        credentials = self.authenticate()

        return build(
            "gmail",
            "v1",
            credentials=credentials,
        )

    def iter_message_ids(
        self,
        *,
        query: str = "",
        max_results: int = 25,
    ) -> Iterator[str]:
        service = self.build_service()

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query or None,
                maxResults=max_results,
            )
            .execute()
        )

        for message in response.get(
            "messages",
            [],
        ):
            message_id = message.get("id")

            if message_id:
                yield message_id

    def get_raw_message(
        self,
        message_id: str,
    ) -> bytes:
        service = self.build_service()

        response = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="raw",
            )
            .execute()
        )

        encoded_message = response["raw"]

        padding = "=" * (
            -len(encoded_message) % 4
        )

        return base64.urlsafe_b64decode(
            encoded_message + padding
        )