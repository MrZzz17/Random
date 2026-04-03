"""
Summarize unread Gmail inbox: sender, subject, and date.
Usage: python triage.py
"""

import os
import base64
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "../../config/credentials.json"
TOKEN_FILE = "../../config/token.json"


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def get_header(headers, name):
    return next((h["value"] for h in headers if h["name"].lower() == name.lower()), "")


def triage(max_results=20):
    service = get_service()
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print("Inbox is clear!")
        return

    print(f"\n{'#':<4} {'From':<35} {'Subject':<50} {'Date'}")
    print("-" * 105)

    for i, msg_ref in enumerate(messages, 1):
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = msg["payload"]["headers"]
        sender = get_header(headers, "From")[:33]
        subject = get_header(headers, "Subject")[:48]
        date = get_header(headers, "Date")[:20]
        print(f"{i:<4} {sender:<35} {subject:<50} {date}")


if __name__ == "__main__":
    triage()
