'''
Servidor MCP que expone las dos herramientas: calculator_agent y gmail_agent.
Utiliza FastMCP para crear un servidor HTTP que maneja estas herramientas, y carga la configuración desde un archivo .env utilizando Pydantic para una gestión de configuración robusta.
'''

from __future__ import annotations

from fastmcp import FastMCP

from app.agents.calculator_agent import answer_math_request
from app.agents.gmail_agent import GmailAgent
from app.config import get_settings

mcp = FastMCP(
    name="Asistente Correo IA MCP",
    instructions=(
        "Servidor MCP con dos agentes: calculator_agent para matemáticas y "
        "gmail_agent para resumir y priorizar correos recientes."
    ),
)

# Llama al agente calculadora 
@mcp.tool(name="calculator_agent")
async def calculator_agent_tool(message: str) -> str:
    return await answer_math_request(message)

# Llama al agente de Gmail 
@mcp.tool(name="gmail_agent")
async def gmail_agent_tool(message: str = "") -> str:
    _ = message
    return await GmailAgent().summarize_recent_emails()

# Arranca el servidor con la configuración especificada en el .env
def main() -> None: 
    settings = get_settings()
    print(
        f"Arrancando servidor MCP en http://{settings.mcp_host}:{settings.mcp_port}{settings.mcp_path}"
    )
    mcp.run(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
        path=settings.mcp_path,
    )


if __name__ == "__main__":
    main()
