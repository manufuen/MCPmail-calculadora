from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client

from app.config import get_settings
from app.services.viewnext_client import ViewnextClient


def _tool_result_to_text(result: Any) -> str:
    """Normaliza la salida de FastMCP Client.call_tool a texto.

    FastMCP 3.x devuelve un CallToolResult con `.data` y `.content`.
    Versiones anteriores podían devolver listas de TextContent.
    """
    if isinstance(result, str):
        return result

    data = getattr(result, "data", None)
    if isinstance(data, str):
        return data

    content = getattr(result, "content", None)
    if isinstance(content, list):
        chunks = []
        for item in content:
            text = getattr(item, "text", None)
            chunks.append(str(text if text is not None else item))
        return "\n".join(chunks)

    if isinstance(result, list):
        chunks = []
        for item in result:
            text = getattr(item, "text", None)
            chunks.append(str(text if text is not None else item))
        return "\n".join(chunks)

    text = getattr(result, "text", None)
    if text is not None:
        return str(text)
    return str(result)


async def handle_user_message(message: str, client: Client, ai_client: ViewnextClient) -> str:
    decision = await ai_client.classify_intent(message)

    if decision.intent == "calculator":
        result = await client.call_tool("calculator_agent", {"message": message})
    else:
        result = await client.call_tool("gmail_agent", {})

    tool_text = _tool_result_to_text(result)
    return (
        f"Agente seleccionado: {decision.intent}\n"
        f"Motivo: {decision.reason} (confianza: {decision.confidence:.2f})\n\n"
        f"{tool_text}"
    )


async def chat_loop() -> None:
    settings = get_settings()
    ai_client = ViewnextClient(settings)

    print("Chatbot MCP por consola")
    print("Escribe 'salir' para terminar.")
    print(f"Conectando con servidor MCP: {settings.mcp_url}\n")

    async with Client(settings.mcp_url) as client:
        while True:
            message = input("Tú > ").strip()
            if message.lower() in {"salir", "exit", "quit", "q"}:
                print("Hasta luego.")
                break
            if not message:
                continue

            try:
                response = await handle_user_message(message, client, ai_client)
                print(f"\nAsistente > {response}\n")
            except Exception as exc:
                print(f"\nError: {exc}\n")
                print(
                    "Comprueba que el servidor MCP esté arrancado con: "
                    "uv run mcp-server\n"
                )


def main() -> None:
    asyncio.run(chat_loop())


if __name__ == "__main__":
    main()
