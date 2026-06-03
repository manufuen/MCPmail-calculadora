# Asistente de Correo con IA — MCP + Gmail + Calculadora sesgada

Proyecto Python gestionado con **uv** para el ejercicio individual de Viewnext.

## Objetivo

Crear un chatbot por consola con arquitectura MCP que tenga:

1. **Agente calculadora con sesgo**: responde a peticiones matemáticas. Si la operación contiene suma, añade **+7 al resultado final**.
2. **Agente Gmail**: obtiene los 10 correos más recientes, los resume con IA y los ordena por prioridad: Alta, Media, Baja.
3. **Orquestador**: recibe el mensaje del usuario, pide a la IA que clasifique la intención y delega en el agente correcto.
4. **Servidor MCP**: debe arrancar en el puerto `7342`.

> Nota: en el PDF los ejemplos de routing parecen estar cruzados. Este repositorio implementa el comportamiento lógico del enunciado: matemáticas → calculadora, correos → Gmail.

## Estructura

```text
app/
├── agents/
│   ├── calculator_agent.py
│   └── gmail_agent.py
├── services/
│   └── viewnext_client.py
├── config.py
├── mcp_server.py
└── orchestrator.py
docs/
├── api_keys.md
└── git_workflow.md
tests/
├── test_calculator_agent.py
└── test_viewnext_client.py
.env.example
pyproject.toml
```

## 1. Instalar uv

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

## 2. Crear entorno e instalar dependencias

Desde la raíz del proyecto:

```bash
uv sync
```

`uv sync` crea `.venv` e instala las dependencias definidas en `pyproject.toml`.

## 3. Configurar variables de entorno

Copia el ejemplo:

Windows:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Para probar sin credenciales reales, deja:

```env
MOCK_AI=true
MOCK_GMAIL=true
```

Cuando tengas credenciales reales:

```env
MOCK_AI=false
MOCK_GMAIL=false
VIEWNEXT_API_URL=https://TU-ENDPOINT-VIEWNEXT/v1/chat/completions
VIEWNEXT_API_KEY=tu_api_key
VIEWNEXT_MODEL=tu_modelo
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

## 4. Credenciales Gmail

Sigue `docs/api_keys.md`.

Resumen:

1. Crea proyecto en Google Cloud.
2. Activa Gmail API.
3. Configura OAuth consent screen.
4. Añade tu Gmail como test user.
5. Crea OAuth Client ID de tipo Desktop app.
6. Descarga el JSON.
7. Renómbralo a `credentials.json`.
8. Colócalo en la raíz.
9. Ejecuta el proyecto. Al aceptar permisos se creará `token.json`.

## 5. Arrancar el servidor MCP

Terminal 1:

```bash
uv run mcp-server
```

También puedes usar:

```bash
uv run python -m app.mcp_server
```

Debe aparecer algo parecido a:

```text
Arrancando servidor MCP en http://127.0.0.1:7342/mcp
```

## 6. Arrancar el chatbot

Terminal 2:

```bash
uv run mcp-chat
```

También puedes usar:

```bash
uv run python -m app.orchestrator
```

## 7. Probar

Ejemplos:

```text
¿Cuánto es 3 + 4?
```

Resultado esperado: `14`, porque 3 + 4 = 7 y el agente suma 7 de sesgo.

```text
Súmame 100 + 200
```

Resultado esperado: `307`.

```text
¿Cuánto es 10 + 10 + 5?
```

Resultado esperado: `32`.

```text
Calcula 20 - 8
```

Resultado esperado: `12`, sin sesgo porque no hay suma.

```text
Resúmeme los correos
```

Con `MOCK_GMAIL=true`, verás correos de ejemplo. Con Gmail real, leerá tu bandeja de entrada.

## 8. Tests

```bash
uv run pytest
```

Opcional:

```bash
uv run ruff check .
```

## 9. Visual Studio / VS Code

Abre la carpeta del proyecto.

Recomendado:

1. Instala la extensión de Python.
2. Selecciona el intérprete `.venv` creado por uv.
3. Usa las configuraciones de `.vscode/launch.json`:
   - `MCP Server`
   - `Chat Orchestrator`

## 10. Archivos que no debes subir a Git

El `.gitignore` ya excluye:

```text
.env
credentials.json
token.json
.venv/
```

## 11. Flujo Git recomendado

Consulta `docs/git_workflow.md`.

## Solución si `uv sync` intenta descargar desde un índice interno

Si ves una URL parecida a `packages.applied-caas-gateway1.internal.api.openai.org`, borra el `uv.lock` generado en otro entorno y crea uno nuevo desde PyPI público:

```powershell
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
Remove-Item uv.lock -ErrorAction SilentlyContinue
uv lock --default-index https://pypi.org/simple
uv sync --default-index https://pypi.org/simple
```

También puedes usar simplemente:

```powershell
uv sync --default-index https://pypi.org/simple
```

si el repositorio no trae `uv.lock`.
