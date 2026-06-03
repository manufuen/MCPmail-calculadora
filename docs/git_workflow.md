# Flujo Git recomendado

El enunciado pide usar Git activamente. Una forma sencilla de demostrarlo:

```bash
git init
git add .
git commit -m "chore: estructura inicial del proyecto con uv"

git add app/agents/calculator_agent.py tests/test_calculator_agent.py
git commit -m "feat: agente calculadora con sesgo de suma"

git add app/services/viewnext_client.py app/orchestrator.py tests/test_viewnext_client.py
git commit -m "feat: orquestador con clasificacion de intencion"

git add app/agents/gmail_agent.py docs/api_keys.md
git commit -m "feat: agente gmail con oauth y resumen por ia"

git add app/mcp_server.py README.md .env.example .vscode/launch.json
git commit -m "feat: servidor mcp en puerto 7342 y documentacion"
```

Antes de cada commit funcional:

```bash
uv run pytest
```

Si usas Ruff:

```bash
uv run ruff check .
```
