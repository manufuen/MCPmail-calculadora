from __future__ import annotations

import asyncio

# Para usar async/await en la función main y en el chat loop, permitiendo operaciones asíncronas como llamadas a herramientas y clasificación de intenciones sin bloquear la ejecución
from typing import Any

from fastmcp import Client

# Para interactuar con el servidor MCP, llamando a las herramientas expuestas por el servidor de forma asíncrona
from app.config import get_settings
from app.services.viewnext_client import ViewnextClient

'''
Chatbot de consola para interactuar con el servidor MCP. Permite al usuario escribir mensajes, clasifica la intención usando ViewnextClient, y llama al agente correspondiente en el servidor MCP según la intención detectada. La respuesta de la herramienta se normaliza a texto y se muestra al usuario junto con información sobre la decisión tomada por el clasificador de intenciones.
'''

def _tool_result_to_text(result: object) -> str:
    """
    Convierte el resultado devuelto por una herramienta MCP a texto legible.

    MCP puede devolver contenido de varios tipos. Normalmente nuestras herramientas
    devuelven texto, pero el tipado contempla imágenes, audio y recursos.
    """

    content = getattr(result, "content", None)

    if not content:
        return str(result)

    parts: list[str] = []

    for item in content:
        text = getattr(item, "text", None)

        if isinstance(text, str):
            parts.append(text)
        else:
            parts.append(str(item))

    return "\n".join(parts)


async def handle_user_message(
    message: str,
    client: Client,
    ai_client: ViewnextClient,
) -> str:
    """
    Maneja un mensaje del usuario.

    1. Clasifica la intención con Viewnext.
    2. Si es 'general', responde directamente con el LLM sin usar agentes MCP.
    3. Si es 'calculator', llama al agente calculadora.
    4. Si es 'gmail', llama al agente Gmail.
    """

    decision = await ai_client.classify_intent(message)

    if decision.intent == "general":
        response = await ai_client.answer_general_question(message)
        return (
            "Ningún agente seleccionado, respuesta generada por el LLM\n\n"
            f"{response}"
        )

    if decision.intent == "calculator":
        result = await client.call_tool(
            "calculator_agent",
            {"message": message},
        )
        return (
            f"Agente seleccionado: {decision.intent}\n\n"
            f"{_tool_result_to_text(result)}"
        )

    if decision.intent == "gmail":
        result = await client.call_tool(
            "gmail_agent",
            {"message": message},
        )
        return (
            f"Agente seleccionado: {decision.intent}\n\n"
            f"{_tool_result_to_text(result)}"
        )

    response = await ai_client.answer_general_question(message)
    return (
        "Ningún agente seleccionado, respuesta generada por el LLM\n\n"
        f"{response}"
    )
    decision = await ai_client.classify_intent(message)

    if decision.intent == "general":
        print("\nNingún agente seleccionado, respuesta generada por el LLM\n")
        response = await ai_client.answer_general_question(message)
        print(response)
        

    print(f"\nAgente seleccionado: {decision.intent}\n")

    if decision.intent == "calculator":
        result = await client.call_tool(
            "calculator_agent",
            {"message": message},
        )
        print(result.content[0].text)
        

    if decision.intent == "gmail":
        result = await client.call_tool(
            "gmail_agent",
            {"message": message},
        )
        print(result.content[0].text)
        


async def chat_loop() -> None:
    # Función principal para el bucle de chat. Carga la configuración, crea un cliente Viewnext para clasificar intenciones, y luego entra en un bucle donde lee mensajes del usuario desde la consola. Para cada mensaje, llama a handle_user_message() para obtener la respuesta del agente correspondiente, y muestra la respuesta al usuario. El bucle continúa hasta que el usuario escribe "salir" o una variante de esa palabra.
    settings = get_settings()
    ai_client = ViewnextClient(settings)

    print("Chatbot MCP por consola")
    print("Escribe 'salir' para terminar de hablar con el chatbot.")
    print(f"Conectando con servidor MCP: {settings.mcp_url}\n")

    async with Client(settings.mcp_url) as client:
        while True:
            message = input("Consulta sobre el mail o dime que calcular > ").strip()
            if message.lower() in {"salir", "exit", "quit", "q"}:
                print("Hasta la próxima!")
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
