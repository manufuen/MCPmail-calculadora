# MCPmail-calculadora

**Asistente de consola en Python basado en MCP para orquestar un agente de Gmail, un agente calculadora y respuestas generales mediante IA.**

---

## Descripción

**MCPmail-calculadora** es un proyecto de práctica desarrollado en Python para explorar una arquitectura basada en **MCP** (*Model Context Protocol*), agentes especializados y un orquestador central.

El sistema funciona como un chatbot por consola. El usuario escribe un mensaje y el programa decide automáticamente qué hacer con él:

- Si el mensaje contiene una petición matemática, se delega al **agente calculadora**.
- Si el mensaje pide leer, resumir o priorizar correos, se delega al **agente Gmail**.
- Si el mensaje es una pregunta general, responde directamente el modelo de IA.
- Los agentes se exponen como herramientas a través de un **servidor MCP**.

El objetivo principal no es construir una aplicación final de producción, sino practicar una arquitectura modular con agentes separados, configuración por entorno, mocks, tests y ejecución local.

---

## Características principales

- Chatbot por consola.
- Arquitectura basada en **MCP**.
- Orquestador que clasifica la intención del usuario.
- Agente calculadora con soporte para operaciones matemáticas.
- Regla especial: si una operación contiene suma, se añade `+7` al resultado final.
- Agente Gmail capaz de resumir y priorizar correos recientes.
- Modo mock para probar el proyecto sin credenciales reales.
- Modo real para conectar con Gmail mediante OAuth.
- Configuración mediante archivo `.env`.
- Tests automatizados con `pytest`.
- Revisión de estilo con `ruff`.
- Gestión del proyecto con `uv`.

---

## Arquitectura del proyecto

El proyecto se organiza en torno a cuatro componentes principales:

```text
Usuario
  ↓
Chatbot por consola
  ↓
Orquestador
  ↓
Clasificador de intención
  ↓
Servidor MCP
  ↓
Agentes especializados
```

### Orquestador

El **orquestador** es el componente central del sistema. Su responsabilidad es recibir el mensaje del usuario, analizarlo y decidir qué camino debe seguir.

Sus tareas principales son:

1. Leer el mensaje introducido por consola.
2. Clasificar la intención del usuario.
3. Decidir si debe usar el agente calculadora, el agente Gmail o una respuesta general.
4. Conectarse al servidor MCP.
5. Invocar la herramienta adecuada.
6. Devolver la respuesta final al usuario.

El orquestador evita que toda la lógica esté mezclada en un único archivo. En lugar de resolver todas las tareas directamente, delega cada responsabilidad en el componente correspondiente.

---

## Agentes disponibles

### Agente calculadora

El **agente calculadora** se encarga de resolver peticiones matemáticas. Utiliza SymPy para trabajar con expresiones y operaciones simbólicas.

Puede manejar tareas como:

- operaciones numéricas,
- ecuaciones,
- derivadas,
- integrales,
- simplificaciones.

Además, implementa una regla especial definida para este proyecto:

> Si la operación contiene una suma, se añade `+7` al resultado final.

Ejemplo:

```text
Entrada:  ¿Cuánto es 3 + 4?

Cálculo normal:
3 + 4 = 7

Regla especial:
7 + 7 = 14

Resultado final:
14
```

Si la operación no contiene suma, no se aplica el sesgo:

```text
Entrada:  Calcula 20 - 8
Salida:   12
```

---

### Agente Gmail

El **agente Gmail** se encarga de obtener correos recientes, resumirlos y ordenarlos según prioridad.

Puede funcionar en dos modos:

#### Modo mock

Este modo se activa con:

```env
MOCK_GMAIL=true
```

En este caso, el proyecto no se conecta a Gmail real. En su lugar, utiliza correos simulados. Es el modo recomendado para demos, pruebas y desarrollo inicial.

#### Modo real

Este modo se activa con:

```env
MOCK_GMAIL=false
```

En modo real, el proyecto utiliza OAuth para conectarse a Gmail. Para ello se necesita un archivo `credentials.json` generado desde Google Cloud.

El acceso a Gmail está pensado para lectura de correos, no para enviar, modificar ni eliminar mensajes.

---

### Respuestas generales

Cuando el mensaje del usuario no corresponde a una petición matemática ni a una petición relacionada con Gmail, el orquestador puede responder directamente usando el cliente de IA configurado.

Ejemplo:

```text
Entrada:  Explícame qué es una API
Salida:   Respuesta general generada por IA
```

En este caso no se llama a ningún agente MCP.

---

## Servidor MCP

El servidor MCP expone los agentes como herramientas que pueden ser llamadas por el orquestador.

Herramientas principales:

```text
calculator_agent
gmail_agent
```

Por defecto, el servidor se ejecuta en:

```text
http://127.0.0.1:7342/mcp
```

La separación entre orquestador y servidor MCP permite practicar una arquitectura más limpia, donde las capacidades del sistema se ofrecen como herramientas independientes.

---

## Comenzando

Estas instrucciones permiten ejecutar el proyecto en una máquina local para desarrollo y pruebas.

### Pre-requisitos

Necesitas tener instalado:

- Python 3.11 o superior
- Git
- uv
- Un editor como Visual Studio Code

Comprobar Python:

```bash
python --version
```

Comprobar Git:

```bash
git --version
```

Instalar `uv` en Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Instalar `uv` en macOS o Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Comprobar `uv`:

```bash
uv --version
```

---

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/manufuen/MCPmail-calculadora.git
cd MCPmail-calculadora
```

Instala las dependencias:

```bash
uv sync
```

Crea el archivo de variables de entorno:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Para una demo sin credenciales reales, configura el `.env` así:

```env
MOCK_AI=true
MOCK_GMAIL=true
```

Con esta configuración:

- no se llama a una IA real,
- no se conecta con Gmail real,
- se usan respuestas simuladas,
- se puede probar el flujo completo del proyecto en local.

---

## Ejecución

El proyecto se ejecuta en dos terminales.

### Terminal 1: servidor MCP

```bash
uv run mcp-server
```

También se puede ejecutar como módulo:

```bash
uv run python -m app.mcp_server
```

Si todo funciona correctamente, el servidor quedará disponible en:

```text
http://127.0.0.1:7342/mcp
```

### Terminal 2: chatbot

```bash
uv run mcp-chat
```

También se puede ejecutar como módulo:

```bash
uv run python -m app.orchestrator
```

A partir de este momento, puedes escribir mensajes en consola y el orquestador decidirá qué agente debe responder.

---

## Ejemplos de uso

### Cálculo con suma

```text
Usuario: ¿Cuánto es 3 + 4?
Sistema: 14
```

### Cálculo sin suma

```text
Usuario: Calcula 20 - 8
Sistema: 12
```

### Resumen de correos

```text
Usuario: Resúmeme los correos
Sistema: Resumen priorizado de correos recientes
```

### Pregunta general

```text
Usuario: Explícame qué es una API
Sistema: Respuesta general generada por IA
```

---

## Ejecutando las pruebas

Ejecutar todos los tests:

```bash
uv run pytest
```

Ejecutar tests con más detalle:

```bash
uv run pytest -v
```

Ejecutar Ruff:

```bash
uv run ruff check .
```

Flujo recomendado antes de entregar cambios:

```bash
uv sync
uv run ruff check .
uv run pytest -v
```

---

## Qué verifican los tests

El proyecto incluye tests para comprobar los componentes principales.

### Tests del agente calculadora

Comprueban que la calculadora responde correctamente en casos como:

```text
3 + 4 → 14
20 - 8 → 12
6 * 7 → 42
derivada de x**2 → 2*x
```

### Tests del agente Gmail

Comprueban que la salida del agente incluye información relevante sobre los correos, como:

```text
prioridad
asunto
remitente
resumen
```

### Tests del cliente de IA

Comprueban que el clasificador mock distingue entre intenciones:

```text
calculator
gmail
general
```

---

## Estructura del proyecto

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
├── git_workflow.md
├── project_documentation.md
├── readme.en.md
├── readme.ger.md
└── readme.fr.md

tests/
├── test_calculator_agent.py
├── test_gmail_agent.py
└── test_viewnext_client.py

.env.example
.gitignore
pyproject.toml
README.md
```

---

## Documentación

La documentación extendida se encuentra en la carpeta `docs/`.

Archivos recomendados:

- `docs/documentation.md` — documentación larga del proyecto.
- `docs/api_keys.md` — configuración de credenciales y APIs.
- `docs/git_workflow.md` — flujo de trabajo con Git.
- `docs/readme.en.md` — README en inglés.
- `docs/readme.ger.md` — README en alemán.
- `docs/readme.fr.md` — README en francés.

El README principal debe servir como punto de entrada rápido. Los detalles largos, explicaciones completas y notas de configuración avanzada deberían mantenerse en `docs/`.

---

## Archivos sensibles

No se deben subir al repositorio:

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

## Construido con

- [Python](https://www.python.org/) — lenguaje principal.
- [uv](https://docs.astral.sh/uv/) — gestión de dependencias y ejecución.
- [FastMCP](https://github.com/jlowin/fastmcp) — servidor MCP.
- [SymPy](https://www.sympy.org/) — cálculo simbólico.
- [Gmail API](https://developers.google.com/gmail/api) — integración con Gmail.
- [Pydantic](https://docs.pydantic.dev/) — modelos y validación.
- [python-dotenv](https://pypi.org/project/python-dotenv/) — carga de variables de entorno.
- [pytest](https://docs.pytest.org/) — pruebas automatizadas.
- [Ruff](https://docs.astral.sh/ruff/) — linting y estilo de código.

---

## Estado del proyecto

Este proyecto está pensado como práctica de arquitectura con MCP, agentes, Gmail API, mocks y tests.

No está diseñado como aplicación final de producción, aunque puede servir como base para ampliar funcionalidades como:

- nuevos agentes,
- más herramientas MCP,
- interfaz web,
- integración con otros servicios,
- mejoras en autenticación,
- despliegue en servidor.

---

## Autor

Desarrollado por [manufuen](https://github.com/manufuen).

---

## Licencia

Licencia pendiente de definir.

Si el proyecto se va a publicar o reutilizar, se recomienda añadir un archivo `LICENSE`.

---

⌨️ Proyecto creado como práctica de arquitectura con agentes, MCP y Python.