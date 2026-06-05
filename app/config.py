""" 
Configuración centralizada para la aplicación, cargando variables de entorno desde un archivo .env y proporcionando una clase de configuración inmutable.
"""
# importamos las librerías necesarias para manejar la configuración, incluyendo os para acceder a las variables de entorno, dataclasses para crear una clase de configuración inmutable, functools para usar lru_cache y pathlib para manejar rutas de archivos. También importamos load_dotenv de dotenv para cargar las variables de entorno desde un archivo .env.
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent # Directorio base del proyecto, útil para construir rutas relativas a partir de la ubicación de este archivo.


def _bool_env(name: str, default: bool = False) -> bool:
    # Convierte una variable de entorno a booleano, considerando varias formas comunes de representar "true". Si la variable no está definida, devuelve el valor por defecto.
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on", "si", "sí"}


@dataclass(frozen=True) # Decorador para crear una clase de configuración inmutable, lo que garantiza que los valores no cambien en tiempo de ejecución y facilita su uso en toda la aplicación.
class Settings: # Clase de configuración inmutable que contiene todas las variables necesarias para la aplicación, agrupando la configuración relacionada con el MCP, Viewnext y Gmail.
    mcp_host: str
    mcp_port: int
    mcp_path: str
    mcp_url: str

    viewnext_provider: str
    viewnext_origin: str
    viewnext_origin_detail: str

    viewnext_api_url: str
    viewnext_api_key: str
    viewnext_model: str
    viewnext_timeout_seconds: float
    mock_ai: bool

    google_credentials_file: Path
    google_token_file: Path
    gmail_max_results: int
    mock_gmail: bool


@lru_cache(maxsize=1) # Cachea la función para que solo se ejecute una vez, evitando cargar el .env y crear la configuración cada vez que se llama a get_settings(), lo que mejora el rendimiento.
def get_settings() -> Settings: # Función que carga la configuración desde el archivo .env y devuelve una instancia de Settings. Al usar lru_cache, esta función solo se ejecutará una vez, y las llamadas posteriores devolverán la misma instancia de Settings sin volver a cargar el .env.
    load_dotenv(BASE_DIR / ".env")

    mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp_port = int(os.getenv("MCP_PORT", "7342"))
    mcp_path = os.getenv("MCP_PATH", "/mcp")
    mcp_url = os.getenv("MCP_URL", f"http://{mcp_host}:{mcp_port}{mcp_path}")

    return Settings(
        mcp_host=mcp_host,
        mcp_port=mcp_port,
        mcp_path=mcp_path,
        mcp_url=mcp_url,

        viewnext_provider=os.getenv("VIEWNEXT_PROVIDER", "AzureOpenAI"),
        viewnext_origin=os.getenv("VIEWNEXT_ORIGIN", "asistente-correo-mcp"),
        viewnext_origin_detail=os.getenv(
            "VIEWNEXT_ORIGIN_DETAIL",
            "proyecto-becarios-gmail-agent",
        ),
        
        viewnext_api_url=os.getenv("VIEWNEXT_API_URL", ""),
        viewnext_api_key=os.getenv("VIEWNEXT_API_KEY", ""),
        viewnext_model=os.getenv("VIEWNEXT_MODEL", ""),
        viewnext_timeout_seconds=float(os.getenv("VIEWNEXT_TIMEOUT_SECONDS", "60")),
        mock_ai=_bool_env("MOCK_AI", default=True),
        google_credentials_file=BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
        google_token_file=BASE_DIR / os.getenv("GOOGLE_TOKEN_FILE", "token.json"),
        gmail_max_results=int(os.getenv("GMAIL_MAX_RESULTS", "10")),
        mock_gmail=_bool_env("MOCK_GMAIL", default=True),
    )
