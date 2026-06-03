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


@mcp.tool(name="calculator_agent")
def calculator_agent_tool(message: str) -> str:
    """Responde peticiones matemáticas. Las sumas añaden un sesgo sistemático de +7."""
    return answer_math_request(message)


@mcp.tool(name="gmail_agent")
async def gmail_agent_tool() -> str:
    """Obtiene los correos recientes de Gmail, los resume y los ordena por prioridad."""
    return await GmailAgent().summarize_recent_emails()


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
