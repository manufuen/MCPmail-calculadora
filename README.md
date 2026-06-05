# Asistente de Correo con IA — MCP + Gmail + Calculadora sesgada

Proyecto Python gestionado con **uv** para practicar una arquitectura basada en **MCP** con dos agentes:

1. **Agente calculadora**: responde a peticiones matemáticas. Si la operación contiene suma, añade **+7 al resultado final**.
2. **Agente Gmail**: obtiene correos recientes, los resume con IA y los ordena por prioridad.
3. **Orquestador**: recibe el mensaje del usuario, clasifica la intención y delega en el agente correcto.
4. **Servidor MCP**: expone los agentes como herramientas MCP en el puerto `7342`.

> Nota: el objetivo del proyecto es practicar el uso de MCP con agentes separados. No pretende ser una aplicación final de producción, sino una práctica completa de orquestación, configuración, herramientas, mocks, tests y ejecución por consola.

---

## 1. Objetivo del proyecto

El objetivo es construir un chatbot por consola que pueda recibir mensajes del usuario y decidir qué hacer con ellos:

- Si el usuario pide un cálculo, se llama al **agente calculadora**.
- Si el usuario pide leer o resumir correos, se llama al **agente Gmail**.
- Si el usuario hace una pregunta general, responde directamente el LLM sin usar agentes MCP.

Flujo general:

```text
Usuario
  ↓
Orquestador
  ↓
Clasificador de intención
  ↓
Decisión:
  - calculator → calculator_agent vía MCP
  - gmail → gmail_agent vía MCP
  - general → respuesta directa del LLM
```

---

## 2. Arquitectura

El proyecto está dividido en varias capas:

```text
Chatbot por consola
  ↓
orchestrator.py
  ↓
ViewnextClient clasifica intención
  ↓
Servidor MCP
  ↓
Agentes:
  - calculator_agent
  - gmail_agent
```

La idea principal es que el orquestador no resuelve todas las tareas directamente. Su responsabilidad es:

1. Recibir el mensaje.
2. Clasificar la intención.
3. Delegar en el agente correspondiente.

---

## 3. Estructura del proyecto

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
├── test_gmail_agent.py
└── test_viewnext_client.py

.vscode/
└── launch.json

.env.example
.gitignore
pyproject.toml
README.md
```

---

## 4. Explicación de archivos principales

### `pyproject.toml`

Define la configuración del proyecto Python:

- Nombre del proyecto.
- Versión.
- Dependencias.
- Scripts ejecutables.
- Configuración de pytest.
- Configuración de Ruff.

Scripts principales:

```toml
mcp-server = "app.mcp_server:main"
mcp-chat = "app.orchestrator:main"
```

Gracias a esto se puede ejecutar:

```bash
uv run mcp-server
uv run mcp-chat
```

---

### `.env.example`

Plantilla de variables de entorno.

Sirve para crear el archivo `.env` real:

```bash
cp .env.example .env
```

Variables principales:

```env
MCP_HOST=127.0.0.1
MCP_PORT=7342
MCP_PATH=/mcp
MCP_URL=http://127.0.0.1:7342/mcp

MOCK_AI=true
MOCK_GMAIL=true

VIEWNEXT_API_URL=
VIEWNEXT_API_KEY=
VIEWNEXT_MODEL=
VIEWNEXT_TIMEOUT_SECONDS=60

VIEWNEXT_PROVIDER=AzureOpenAI
VIEWNEXT_ORIGIN=asistente-correo-mcp
VIEWNEXT_ORIGIN_DETAIL=proyecto-becarios-gmail-agent

GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GMAIL_MAX_RESULTS=10
```

Para una demo sin credenciales reales, se recomienda dejar:

```env
MOCK_AI=true
MOCK_GMAIL=true
```

---

### `app/config.py`

Centraliza la configuración del proyecto.

Sus responsabilidades son:

- Cargar variables desde `.env`.
- Definir rutas base.
- Convertir variables de entorno a tipos adecuados.
- Crear un objeto `Settings`.
- Cachear la configuración con `lru_cache`.

El resto del proyecto usa:

```python
settings = get_settings()
```

para acceder a configuración como:

```text
MCP_HOST
MCP_PORT
MCP_URL
MOCK_AI
MOCK_GMAIL
VIEWNEXT_API_URL
GOOGLE_CREDENTIALS_FILE
```

---

### `app/mcp_server.py`

Crea el servidor MCP con FastMCP y expone dos herramientas:

```python
calculator_agent
gmail_agent
```

El agente calculadora se registra así:

```python
@mcp.tool(name="calculator_agent")
async def calculator_agent_tool(message: str) -> str:
    return await answer_math_request(message)
```

El agente Gmail se registra así:

```python
@mcp.tool(name="gmail_agent")
async def gmail_agent_tool(message: str = "") -> str:
    _ = message
    return await GmailAgent().summarize_recent_emails()
```

La función `main()` arranca el servidor MCP en:

```text
http://127.0.0.1:7342/mcp
```

---

### `app/orchestrator.py`

Es el cerebro del chatbot.

Contiene dos partes principales:

#### `handle_user_message()`

Recibe el mensaje del usuario y decide qué hacer:

```text
1. Clasifica la intención.
2. Si es general, responde con el LLM.
3. Si es calculator, llama a calculator_agent vía MCP.
4. Si es gmail, llama a gmail_agent vía MCP.
```

#### `chat_loop()`

Abre el bucle de consola:

```text
1. Carga configuración.
2. Crea cliente Viewnext.
3. Se conecta al servidor MCP.
4. Lee mensajes del usuario.
5. Llama a handle_user_message().
6. Muestra la respuesta.
```

---

### `app/services/viewnext_client.py`

Cliente encargado de la interacción con la IA.

Responsabilidades:

- Clasificar intención.
- Traducir lenguaje natural matemático a expresiones compatibles con SymPy.
- Responder preguntas generales.
- Resumir y priorizar correos.
- Llamar al endpoint real de Viewnext cuando `MOCK_AI=false`.
- Usar lógica local simulada cuando `MOCK_AI=true`.

Define dos estructuras importantes:

```python
RouteDecision
MathTranslation
```

`RouteDecision` representa la decisión del router:

```text
intent
confidence
reason
```

`MathTranslation` representa una petición matemática traducida:

```text
kind
expression
variable
lower_bound
upper_bound
explanation
```

---

### `app/agents/calculator_agent.py`

Agente encargado de cálculos matemáticos.

Usa **SymPy** para soportar:

```text
expresiones numéricas
ecuaciones
derivadas
integrales
simplificaciones
```

Funciones permitidas:

```text
sqrt
log
ln
sin
cos
tan
asin
acos
atan
abs
factorial
pi
e
```

Además aplica la regla especial de la tarea:

> Si la expresión contiene suma, se añade **+7** al resultado final.

Ejemplo:

```text
3 + 4 = 7
7 + 7 = 14
```

Función importante:

```python
calculate_translation()
```

Esta función recibe una `MathTranslation` y decide qué operación ejecutar.

---

### `app/agents/gmail_agent.py`

Agente encargado de Gmail.

Puede funcionar de dos formas:

#### Modo mock

Si `MOCK_GMAIL=true`, no se conecta a Gmail real. Usa correos de ejemplo.

Esto es ideal para demos y pruebas.

#### Modo real

Si `MOCK_GMAIL=false`, usa OAuth con Gmail.

El scope utilizado es:

```text
https://www.googleapis.com/auth/gmail.readonly
```

Es decir, solo tiene permiso de lectura.

Flujo real:

```text
1. Busca token.json.
2. Si existe y es válido, lo usa.
3. Si está expirado, lo refresca.
4. Si no existe, usa credentials.json para abrir OAuth.
5. Lee correos recientes de INBOX.
6. Extrae remitente, asunto, fecha, snippet y cuerpo.
7. Envía los correos a la IA para resumir y priorizar.
```

---

## 5. Instalación

### 5.1 Instalar uv

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

---

### 5.2 Clonar el repositorio

```bash
git clone https://github.com/manufuen/MCPmail-calculadora.git
cd MCPmail-calculadora
```

Si vas a trabajar con la rama de desarrollo:

```bash
git checkout dev
```

---

### 5.3 Instalar dependencias

Desde la raíz del proyecto:

```bash
uv sync
```

Esto crea `.venv` e instala las dependencias definidas en `pyproject.toml`.

---

### 5.4 Crear archivo `.env`

Windows:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Para una demo sin credenciales reales:

```env
MOCK_AI=true
MOCK_GMAIL=true
```

Para uso real:

```env
MOCK_AI=false
MOCK_GMAIL=false
VIEWNEXT_API_URL=https://TU-ENDPOINT-VIEWNEXT/v1/chat/completions
VIEWNEXT_API_KEY=tu_api_key
VIEWNEXT_MODEL=tu_modelo
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

---

## 6. Configuración de Gmail real

Para usar Gmail real:

1. Crear proyecto en Google Cloud.
2. Activar Gmail API.
3. Configurar OAuth consent screen.
4. Añadir tu Gmail como test user.
5. Crear OAuth Client ID de tipo Desktop App.
6. Descargar el JSON.
7. Renombrarlo a `credentials.json`.
8. Colocarlo en la raíz del proyecto.
9. Ejecutar el chatbot.
10. Aceptar permisos en el navegador.
11. Se generará `token.json`.

Los archivos sensibles no deben subirse a Git.

---

## 7. Ejecución

Se necesitan dos terminales.

### Terminal 1: servidor MCP

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

---

### Terminal 2: chatbot

```bash
uv run mcp-chat
```

También puedes usar:

```bash
uv run python -m app.orchestrator
```

---

## 8. Ejemplos de uso

### Suma con sesgo

Entrada:

```text
¿Cuánto es 3 + 4?
```

Resultado esperado:

```text
14
```

Explicación:

```text
3 + 4 = 7
Como hay suma, se aplica +7
Resultado final = 14
```

---

### Suma mayor

Entrada:

```text
Súmame 100 + 200
```

Resultado esperado:

```text
307
```

---

### Resta sin sesgo

Entrada:

```text
Calcula 20 - 8
```

Resultado esperado:

```text
12
```

No se aplica sesgo porque no hay suma.

---

### Correos

Entrada:

```text
Resúmeme los correos
```

Con `MOCK_GMAIL=true`, se mostrarán correos de ejemplo.

Con `MOCK_GMAIL=false`, se leerán correos reales de Gmail.

---

### Pregunta general

Entrada:

```text
Explícame qué es una API
```

En este caso no se llama a ningún agente MCP. El sistema responde directamente con el LLM.

---

## 9. Tests

Ejecutar todos los tests:

```bash
uv run pytest
```

Con más detalle:

```bash
uv run pytest -v
```

Ejecutar Ruff:

```bash
uv run ruff check .
```

Flujo recomendado antes de entregar:

```bash
git checkout dev
uv sync
uv run ruff check .
uv run pytest -v
```

---

## 10. Qué comprueban los tests

### `tests/test_calculator_agent.py`

Comprueba que la calculadora funciona correctamente:

```text
3+4 → 14
10+10+5 → 32
20-8 → 12
6*7 → 42
2+3*4 → 21
derivada de x**2 → 2*x
x + 2 = 5 → 3
```

### `tests/test_viewnext_client.py`

Comprueba el clasificador mock:

```text
Súmame 2+2 → calculator
Resúmeme los correos → gmail
Explícame qué es una API → general
```

### `tests/test_gmail_agent.py`

Comprueba que el formato de correos priorizados incluye:

```text
prioridad
asunto
remitente
resumen
```

---

## 11. Visual Studio Code

El proyecto incluye configuración de depuración en:

```text
.vscode/launch.json
```

Configuraciones disponibles:

```text
MCP Server
Chat Orchestrator
```

Recomendado:

1. Abrir la carpeta del proyecto en VS Code.
2. Instalar la extensión de Python.
3. Seleccionar el intérprete de `.venv`.
4. Usar las configuraciones de depuración.

---

## 12. Archivos que no debes subir a Git

No se deben subir:

```text
.env
credentials.json
token.json
.venv/
```

Motivo:

- `.env` puede contener claves privadas.
- `credentials.json` contiene credenciales OAuth.
- `token.json` puede permitir acceso a Gmail.
- `.venv/` es el entorno virtual local.

---

## 13. Errores frecuentes

### `uv` no se reconoce

Significa que uv no está instalado o no está en el PATH.

Solución en Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Después, cerrar y abrir PowerShell.

---

### El chatbot no conecta con MCP

Probablemente no está arrancado el servidor MCP.

Solución:

Terminal 1:

```bash
uv run mcp-server
```

Terminal 2:

```bash
uv run mcp-chat
```

---

### Falta `VIEWNEXT_API_URL`

Ocurre si tienes:

```env
MOCK_AI=false
```

pero no has configurado:

```env
VIEWNEXT_API_URL
VIEWNEXT_API_KEY
VIEWNEXT_MODEL
```

Para demo:

```env
MOCK_AI=true
```

---

### Falta `credentials.json`

Ocurre si tienes:

```env
MOCK_GMAIL=false
```

pero no has descargado las credenciales OAuth.

Para demo:

```env
MOCK_GMAIL=true
```

---

### Gmail no autentica

Revisar:

```text
Gmail API activada
OAuth consent screen configurado
Usuario añadido como test user
OAuth Client ID de tipo Desktop App
credentials.json en la raíz
```

---

## 14. Hoja de ruta del proyecto

### Fase 1: Preparar proyecto Python

```text
Crear estructura de carpetas.
Configurar pyproject.toml.
Añadir uv.
Añadir dependencias.
Crear scripts mcp-server y mcp-chat.
```

### Fase 2: Configuración

```text
Crear config.py.
Cargar .env.
Definir Settings.
Añadir .env.example.
Separar modo mock y modo real.
```

### Fase 3: Agente calculadora

```text
Crear calculator_agent.py.
Usar SymPy.
Validar expresiones.
Añadir sesgo +7 en sumas.
Soportar ecuaciones, derivadas, integrales y simplificaciones.
```

### Fase 4: Agente Gmail

```text
Crear gmail_agent.py.
Añadir modo mock.
Añadir OAuth Gmail.
Leer últimos correos.
Extraer remitente, asunto, fecha, snippet y cuerpo.
```

### Fase 5: Servicio de IA

```text
Crear viewnext_client.py.
Clasificar intención.
Traducir matemáticas.
Responder preguntas generales.
Resumir y priorizar correos.
Parsear JSON del modelo.
```

### Fase 6: Servidor MCP

```text
Crear mcp_server.py.
Registrar calculator_agent.
Registrar gmail_agent.
Arrancar FastMCP por HTTP.
Exponerlo en /mcp puerto 7342.
```

### Fase 7: Orquestador

```text
Crear orchestrator.py.
Conectar con servidor MCP.
Leer mensajes por consola.
Clasificar intención.
Delegar al agente correspondiente.
Mostrar respuesta.
```

### Fase 8: Tests y limpieza

```text
Crear tests de calculadora.
Crear tests del clasificador mock.
Crear tests de Gmail.
Ejecutar pytest.
Ejecutar ruff.
Limpiar código.
```

---

## 15. Guion rápido de presentación

### 1. Introducción

Este proyecto es un chatbot por consola en Python para practicar MCP con dos agentes: una calculadora y un lector/resumidor de Gmail.

### 2. Arquitectura

El usuario escribe una consulta. El orquestador clasifica la intención y decide si llama al agente calculadora, al agente Gmail o si responde directamente con el LLM.

### 3. Servidor MCP

`mcp_server.py` expone dos herramientas:

```text
calculator_agent
gmail_agent
```

### 4. Orquestador

`orchestrator.py` conecta con el servidor MCP y delega tareas.

### 5. Calculadora

`calculator_agent.py` usa SymPy y aplica el sesgo de `+7` cuando hay suma.

### 6. Gmail

`gmail_agent.py` puede usar correos simulados o Gmail real mediante OAuth.

### 7. Configuración

`.env.example` permite trabajar con mocks o credenciales reales.

### 8. Tests

Los tests validan la calculadora, el clasificador mock y el formato de Gmail.

### 9. Demo

Probar:

```text
¿Cuánto es 3 + 4?
Calcula 20 - 8
Resúmeme los correos
Explícame qué es una API
```

---

## 16. Mejoras futuras

Posibles ampliaciones:

```text
Añadir más agentes.
Añadir interfaz web.
Añadir tests del orquestador.
Permitir filtrar correos por remitente o fecha.
Añadir logs estructurados.
Añadir Docker.
Añadir GitHub Actions.
Mejorar la seguridad del parser matemático.
Añadir funcionalidad para responder correos.
```

---

## 17. Resumen final

Este proyecto es un chatbot de consola en Python, gestionado con uv, que usa MCP para exponer dos agentes:

```text
calculator_agent
gmail_agent
```

El orquestador clasifica cada mensaje con IA y decide si debe llamar al agente calculadora, al agente Gmail o responder directamente como pregunta general.

Incluye:

```text
configuración por .env
modo mock para demos sin credenciales
servidor MCP
cliente MCP
dos agentes especializados
tests automáticos
separación clara de responsabilidades
```

El objetivo principal es practicar una arquitectura basada en MCP con agentes separados.
