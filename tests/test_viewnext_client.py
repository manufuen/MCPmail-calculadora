import asyncio
from pathlib import Path

from app.config import Settings
from app.services.viewnext_client import ViewnextClient


def _settings() -> Settings:
    return Settings(
        mcp_host="127.0.0.1",
        mcp_port=7342,
        mcp_path="/mcp",
        mcp_url="http://127.0.0.1:7342/mcp",
        viewnext_provider="AzureOpenAI",
        viewnext_origin="asistente-correo-mcp",
        viewnext_origin_detail="proyecto-becarios-gmail-agent",
        viewnext_api_url="",
        viewnext_api_key="",
        viewnext_model="",
        viewnext_timeout_seconds=60,
        mock_ai=True,
        google_credentials_file=Path("credentials.json"),
        google_token_file=Path("token.json"),
        gmail_max_results=10,
        mock_gmail=True,
    )


async def _classify(message: str):
    return await ViewnextClient(_settings()).classify_intent(message)


def test_mock_router_detects_calculator():
    decision = asyncio.run(_classify("Súmame 2+2"))
    assert decision.intent == "calculator"


def test_mock_router_detects_gmail():
    decision = asyncio.run(_classify("Resúmeme los correos"))
    assert decision.intent == "gmail"


def test_mock_router_detects_general():
    decision = asyncio.run(_classify("Explícame qué es una API"))
    assert decision.intent == "general"