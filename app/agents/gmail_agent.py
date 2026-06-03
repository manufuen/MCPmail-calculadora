from __future__ import annotations

import base64
from email.header import decode_header, make_header
from typing import Any

from app.config import Settings, get_settings
from app.services.viewnext_client import ViewnextClient

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def _get_header(payload: dict[str, Any], name: str) -> str:
    headers = payload.get("headers", [])
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return _decode_header_value(header.get("value"))
    return ""


def _decode_body_data(data: str) -> str:
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_text_from_payload(payload: dict[str, Any]) -> str:
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data", "")

    if mime_type == "text/plain" and body_data:
        return _decode_body_data(body_data)

    parts = payload.get("parts", [])
    for part in parts:
        text = _extract_text_from_payload(part)
        if text:
            return text

    if body_data:
        return _decode_body_data(body_data)

    return ""


def _get_gmail_service(settings: Settings):
    # Imports diferidos para que MOCK_GMAIL=true funcione aunque aún no hayas configurado Google.
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if settings.google_token_file.exists():
        creds = Credentials.from_authorized_user_file(str(settings.google_token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not settings.google_credentials_file.exists():
                raise FileNotFoundError(
                    f"No existe {settings.google_credentials_file}. Descarga el OAuth Client JSON "
                    "desde Google Cloud y renómbralo a credentials.json."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.google_credentials_file), SCOPES
            )
            creds = flow.run_local_server(port=0)

        settings.google_token_file.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def _mock_recent_emails() -> list[dict[str, str]]:
    return [
        {
            "sender": "tutor.viewnext@example.com",
            "subject": "Urgente: revisión del proyecto MCP hoy",
            "snippet": "Necesito que revises el arranque del servidor MCP en el puerto 7342 antes de la reunión de hoy.",
            "body": "Necesito que revises el arranque del servidor MCP en el puerto 7342 antes de la reunión de hoy.",
        },
        {
            "sender": "rrhh@example.com",
            "subject": "Documentación pendiente",
            "snippet": "Recuerda enviar la documentación pendiente durante esta semana.",
            "body": "Recuerda enviar la documentación pendiente durante esta semana.",
        },
        {
            "sender": "newsletter@example.com",
            "subject": "Noticias tecnológicas de la semana",
            "snippet": "Resumen semanal con novedades de IA y desarrollo.",
            "body": "Resumen semanal con novedades de IA y desarrollo.",
        },
    ]


class GmailAgent:
    def __init__(self, settings: Settings | None = None, ai_client: ViewnextClient | None = None):
        self.settings = settings or get_settings()
        self.ai_client = ai_client or ViewnextClient(self.settings)

    def fetch_recent_emails(self) -> list[dict[str, str]]:
        if self.settings.mock_gmail:
            return _mock_recent_emails()

        service = _get_gmail_service(self.settings)
        response = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=self.settings.gmail_max_results)
            .execute()
        )
        messages = response.get("messages", [])
        emails: list[dict[str, str]] = []

        for item in messages:
            message = (
                service.users()
                .messages()
                .get(userId="me", id=item["id"], format="full")
                .execute()
            )
            payload = message.get("payload", {})
            body = _extract_text_from_payload(payload)
            emails.append(
                {
                    "sender": _get_header(payload, "From") or "Remitente desconocido",
                    "subject": _get_header(payload, "Subject") or "Sin asunto",
                    "date": _get_header(payload, "Date"),
                    "snippet": message.get("snippet", ""),
                    "body": body[:4000],
                }
            )

        return emails

    async def summarize_recent_emails(self) -> str:
        emails = self.fetch_recent_emails()
        if not emails:
            return "No he encontrado correos recientes en la bandeja de entrada."

        summarized = await self.ai_client.summarize_and_prioritize_emails(emails)
        return format_prioritized_emails(summarized)


def format_prioritized_emails(emails: list[dict[str, str]]) -> str:
    lines = ["Correos recientes ordenados por prioridad:\n"]
    for index, email in enumerate(emails, start=1):
        lines.extend(
            [
                f"{index}. [{email.get('priority', 'Baja')}] {email.get('subject', 'Sin asunto')}",
                f"   Remitente: {email.get('sender', 'Remitente desconocido')}",
                f"   Resumen: {email.get('summary', 'Sin resumen.')}",
                "",
            ]
        )
    return "\n".join(lines).strip()
