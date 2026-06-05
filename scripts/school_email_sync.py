#!/usr/bin/env python3
"""
Daily SSIS School Email Sync
Fetches new school emails from Gmail (last 24h) and appends a summary to Notion.

Required env vars:
  GMAIL_TOKEN_JSON   - serialized Google OAuth token (see scripts/get_gmail_token.py)
  NOTION_TOKEN       - Notion integration secret
  ANTHROPIC_API_KEY  - for email summarisation via Claude Haiku
  NOTION_PAGE_ID     - target Notion page (default: the SSIS log page)
"""
import os
import json
import base64
import re
from datetime import datetime, timezone

import anthropic
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from notion_client import Client

NOTION_PAGE_ID = os.environ.get(
    "NOTION_PAGE_ID", "37663bf2fb5c81a1aa46e2bc608b60a4"
)
GMAIL_QUERY = "label:SSIS-School newer_than:1d"
STATUS_EMOJI = {"action_required": "🔴", "in_progress": "🟡", "fyi": "🟢"}


# ── Gmail ────────────────────────────────────────────────────────────────────

def gmail_service():
    raw = os.environ.get("GMAIL_TOKEN_JSON")
    if not raw:
        raise SystemExit("❌  GMAIL_TOKEN_JSON secret is not set. See scripts/get_gmail_token.py")
    data = json.loads(raw)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=data["client_id"],
        client_secret=data["client_secret"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def fetch_new_emails(svc):
    result = svc.users().messages().list(
        userId="me", q=GMAIL_QUERY, maxResults=30
    ).execute()

    emails = []
    for msg in result.get("messages", []):
        data = svc.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        hdrs = {h["name"]: h["value"] for h in data["payload"]["headers"]}
        emails.append({
            "subject":   hdrs.get("Subject", "(no subject)"),
            "sender":    hdrs.get("From", ""),
            "date":      hdrs.get("Date", ""),
            "snippet":   data.get("snippet", ""),
            "thread_id": data["threadId"],
            "link":      f"https://mail.google.com/mail/u/0/#all/{data['threadId']}",
        })
    return emails


# ── Claude Haiku analysis ────────────────────────────────────────────────────

def analyze(email: dict) -> dict:
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": (
                f"Subject: {email['subject']}\n"
                f"From: {email['sender']}\n"
                f"Preview: {email['snippet']}\n\n"
                "Reply with JSON only — no markdown:\n"
                '{"summary":"one sentence ≤15 words","deadline":"date string or null",'
                '"status":"action_required|in_progress|fyi"}'
            ),
        }],
    )
    try:
        return json.loads(resp.content[0].text.strip())
    except Exception:
        return {"summary": email["snippet"][:80], "deadline": None, "status": "fyi"}


# ── Notion update ────────────────────────────────────────────────────────────

def notion_client():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise SystemExit("❌  NOTION_TOKEN secret is not set.")
    return Client(auth=token)


def rich(text, bold=False, url=None):
    node = {"type": "text", "text": {"content": text}}
    if url:
        node["text"]["link"] = {"url": url}
    if bold:
        node["annotations"] = {"bold": True}
    return node


def build_blocks(emails: list) -> list:
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    if not emails:
        return [{
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [rich(f"✅  Checked {today} — no new school emails")],
                "icon": {"emoji": "📭"},
                "color": "gray_background",
            },
        }]

    blocks = [{
        "object": "block", "type": "heading_3",
        "heading_3": {
            "rich_text": [rich(f"📬  {today} — {len(emails)} new email(s)")]
        },
    }]

    for email in emails:
        info = analyze(email)
        emoji = STATUS_EMOJI.get(info.get("status", "fyi"), "📧")
        deadline_text = (
            f"  |  ⏰ Deadline: {info['deadline']}" if info.get("deadline") else ""
        )
        blocks.append({
            "object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    rich(f"{emoji}  "),
                    rich(email["subject"], bold=True, url=email["link"]),
                    rich(f"  —  {info['summary']}{deadline_text}"),
                ]
            },
        })
        print(f"  {emoji}  {email['subject']}")
        print(f"      {info['summary']}{deadline_text}")

    blocks.append({"object": "block", "type": "divider", "divider": {}})
    return blocks


def update_notion(emails: list):
    nc = notion_client()
    blocks = build_blocks(emails)
    nc.blocks.children.append(block_id=NOTION_PAGE_ID, children=blocks)
    print(f"✅  Notion updated — {len(emails)} email(s) logged.")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"SSIS Email Sync — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    svc = gmail_service()
    emails = fetch_new_emails(svc)
    print(f"Found {len(emails)} new school email(s) in the last 24h")
    update_notion(emails)
