from app.config import Settings
from app.services.viewnext_client import ViewnextClient

'''
Tests para verificar que el cliente de Viewnext clasifica correctamente las intenciones de los mensajes, utilizando un mock que simula la respuesta de la API de Viewnext.
'''

def _settings() -> Settings:
    return Settings(
        mcp_host="127.0.0.1",
        mcp_port=7342,
        mcp_path="/mcp",
        mcp_url="http://127.0.0.1:7342/mcp",
        viewnext_api_url="",
        viewnext_api_key="",
        viewnext_model="",
        viewnext_timeout_seconds=60,
        mock_ai=True,
        google_credentials_file="credentials.json",  # type: ignore[arg-type]
        google_token_file="token.json",  # type: ignore[arg-type]
        gmail_max_results=10,
        mock_gmail=True,
    )


async def _classify(message: str):
    return await ViewnextClient(_settings()).classify_intent(message)


def test_mock_router_detects_calculator():
    import asyncio

    decision = asyncio.run(_classify("Súmame 2+2"))
    assert decision.intent == "calculator"


def test_mock_router_detects_gmail():
    import asyncio

    decision = asyncio.run(_classify("Resúmeme los correos"))
    assert decision.intent == "gmail"
