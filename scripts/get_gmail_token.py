#!/usr/bin/env python3
"""
One-time helper: generates GMAIL_TOKEN_JSON for use as a GitHub Actions secret.

Steps:
  1. Go to https://console.cloud.google.com
  2. Create a project → Enable Gmail API
  3. Create OAuth 2.0 credentials (Desktop application) → download JSON as credentials.json
  4. pip install google-auth-oauthlib
  5. python scripts/get_gmail_token.py
  6. Copy the printed JSON into GitHub → Settings → Secrets → GMAIL_TOKEN_JSON
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

token_json = {
    "token":         creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri":     creds.token_uri,
    "client_id":     creds.client_id,
    "client_secret": creds.client_secret,
    "scopes":        list(creds.scopes),
}

print("\n── Copy everything below into GitHub secret GMAIL_TOKEN_JSON ──\n")
print(json.dumps(token_json))
print("\n── end ──\n")
