# MCPmail-calculadora

**Python-Konsolenassistent auf Basis von MCP zur Orchestrierung eines Gmail-Agenten, eines Rechner-Agenten und allgemeiner KI-Antworten.**

---

## Beschreibung

**MCPmail-calculadora** ist ein Python-Übungsprojekt, das entwickelt wurde, um eine Architektur auf Basis von **MCP** (*Model Context Protocol*), spezialisierten Agenten und einem zentralen Orchestrator zu erkunden.

Das System funktioniert als Chatbot in der Konsole. Der Benutzer schreibt eine Nachricht und das Programm entscheidet automatisch, was damit geschehen soll:

- Wenn die Nachricht eine mathematische Anfrage enthält, wird sie an den **Rechner-Agenten** weitergeleitet.
- Wenn die Nachricht das Lesen, Zusammenfassen oder Priorisieren von E-Mails anfordert, wird sie an den **Gmail-Agenten** weitergeleitet.
- Wenn es sich um eine allgemeine Frage handelt, antwortet das KI-Modell direkt.
- Die Agenten werden über einen **MCP-Server** als Werkzeuge bereitgestellt.

Das Hauptziel besteht nicht darin, eine produktionsreife Anwendung zu bauen, sondern eine modulare Architektur mit getrennten Agenten, Umgebungskonfiguration, Mocks, Tests und lokaler Ausführung zu üben.

---

## Hauptfunktionen

- Chatbot für die Konsole.
- Architektur auf Basis von **MCP**.
- Orchestrator zur Klassifikation der Benutzerabsicht.
- Rechner-Agent mit Unterstützung für mathematische Operationen.
- Sonderregel: Wenn eine Operation eine Addition enthält, wird `+7` zum Endergebnis addiert.
- Gmail-Agent zum Zusammenfassen und Priorisieren aktueller E-Mails.
- Mock-Modus zum Testen ohne echte Zugangsdaten.
- Realer Modus zur Verbindung mit Gmail über OAuth.
- Konfiguration über eine `.env`-Datei.
- Automatisierte Tests mit `pytest`.
- Code-Style-Prüfung mit `ruff`.
- Projektverwaltung mit `uv`.

---

## Projektarchitektur

Das Projekt ist um vier Hauptkomponenten herum organisiert:

```text
Benutzer
  ↓
Konsolen-Chatbot
  ↓
Orchestrator
  ↓
Intent-Klassifizierer
  ↓
MCP-Server
  ↓
Spezialisierte Agenten
```

### Orchestrator

Der **Orchestrator** ist die zentrale Komponente des Systems. Seine Aufgabe ist es, die Nachricht des Benutzers zu empfangen, zu analysieren und zu entscheiden, welchen Weg sie nehmen soll.

Seine Hauptaufgaben sind:

1. Die in der Konsole eingegebene Nachricht lesen.
2. Die Absicht des Benutzers klassifizieren.
3. Entscheiden, ob der Rechner-Agent, der Gmail-Agent oder eine allgemeine Antwort verwendet werden soll.
4. Eine Verbindung zum MCP-Server herstellen.
5. Das passende Werkzeug aufrufen.
6. Die finale Antwort an den Benutzer zurückgeben.

Der Orchestrator verhindert, dass die gesamte Logik in einer einzigen Datei vermischt wird. Statt alle Aufgaben direkt selbst zu lösen, delegiert er jede Verantwortung an die passende Komponente.

---

## Verfügbare Agenten

### Rechner-Agent

Der **Rechner-Agent** verarbeitet mathematische Anfragen. Er verwendet SymPy, um mit Ausdrücken und symbolischen Operationen zu arbeiten.

Er kann Aufgaben wie diese verarbeiten:

- numerische Operationen,
- Gleichungen,
- Ableitungen,
- Integrale,
- Vereinfachungen.

Außerdem implementiert er eine spezielle Regel dieses Projekts:

> Wenn die Operation eine Addition enthält, wird `+7` zum Endergebnis addiert.

Beispiel:

```text
Eingabe:  Was ist 3 + 4?

Normale Berechnung:
3 + 4 = 7

Sonderregel:
7 + 7 = 14

Endergebnis:
14
```

Wenn die Operation keine Addition enthält, wird die Sonderregel nicht angewendet:

```text
Eingabe:  Berechne 20 - 8
Ausgabe:  12
```

---

### Gmail-Agent

Der **Gmail-Agent** ruft aktuelle E-Mails ab, fasst sie zusammen und sortiert sie nach Priorität.

Er kann in zwei Modi arbeiten:

#### Mock-Modus

Dieser Modus wird aktiviert mit:

```env
MOCK_GMAIL=true
```

In diesem Fall verbindet sich das Projekt nicht mit einem echten Gmail-Konto. Stattdessen werden simulierte E-Mails verwendet. Dieser Modus wird für Demos, Tests und die erste Entwicklung empfohlen.

#### Realer Modus

Dieser Modus wird aktiviert mit:

```env
MOCK_GMAIL=false
```

Im realen Modus verwendet das Projekt OAuth, um sich mit Gmail zu verbinden. Dafür wird eine `credentials.json`-Datei benötigt, die in Google Cloud erzeugt wird.

Der Gmail-Zugriff ist nur zum Lesen von E-Mails gedacht, nicht zum Senden, Ändern oder Löschen von Nachrichten.

---

### Allgemeine Antworten

Wenn die Benutzernachricht weder eine mathematische Anfrage noch eine Gmail-bezogene Anfrage ist, kann der Orchestrator direkt mit dem konfigurierten KI-Client antworten.

Beispiel:

```text
Eingabe:  Erkläre mir, was eine API ist
Ausgabe:  Allgemeine Antwort, erzeugt durch KI
```

In diesem Fall wird kein MCP-Agent aufgerufen.

---

## MCP-Server

Der MCP-Server stellt die Agenten als Werkzeuge bereit, die vom Orchestrator aufgerufen werden können.

Hauptwerkzeuge:

```text
calculator_agent
gmail_agent
```

Standardmäßig läuft der Server unter:

```text
http://127.0.0.1:7342/mcp
```

Die Trennung zwischen Orchestrator und MCP-Server hilft dabei, eine sauberere Architektur zu üben, in der die Fähigkeiten des Systems als unabhängige Werkzeuge angeboten werden.

---

## Erste Schritte

Diese Anleitung ermöglicht es, das Projekt lokal für Entwicklung und Tests auszuführen.

### Voraussetzungen

Du benötigst:

- Python 3.11 oder höher
- Git
- uv
- Einen Editor wie Visual Studio Code

Python prüfen:

```bash
python --version
```

Git prüfen:

```bash
git --version
```

`uv` unter Windows PowerShell installieren:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uv` unter macOS oder Linux installieren:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` prüfen:

```bash
uv --version
```

---

## Installation

Repository klonen:

```bash
git clone https://github.com/manufuen/MCPmail-calculadora.git
cd MCPmail-calculadora
```

Abhängigkeiten installieren:

```bash
uv sync
```

Datei für Umgebungsvariablen erstellen:

```bash
cp .env.example .env
```

Unter Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Für eine Demo ohne echte Zugangsdaten wird `.env` so konfiguriert:

```env
MOCK_AI=true
MOCK_GMAIL=true
```

Mit dieser Konfiguration:

- wird kein echter KI-Dienst aufgerufen,
- wird kein echtes Gmail-Konto verwendet,
- werden simulierte Antworten genutzt,
- kann der vollständige Projektfluss lokal getestet werden.

---

## Projekt ausführen

Das Projekt wird in zwei Terminals ausgeführt.

### Terminal 1: MCP-Server

```bash
uv run mcp-server
```

Alternativ kann er als Modul ausgeführt werden:

```bash
uv run python -m app.mcp_server
```

Wenn alles korrekt funktioniert, ist der Server verfügbar unter:

```text
http://127.0.0.1:7342/mcp
```

### Terminal 2: Chatbot

```bash
uv run mcp-chat
```

Alternativ kann er als Modul ausgeführt werden:

```bash
uv run python -m app.orchestrator
```

Ab diesem Moment kannst du Nachrichten in die Konsole schreiben, und der Orchestrator entscheidet, welcher Agent antworten soll.

---

## Nutzungsbeispiele

### Berechnung mit Addition

```text
Benutzer: Was ist 3 + 4?
System:   14
```

### Berechnung ohne Addition

```text
Benutzer: Berechne 20 - 8
System:   12
```

### Zusammenfassung von E-Mails

```text
Benutzer: Fasse meine E-Mails zusammen
System:   Priorisierte Zusammenfassung aktueller E-Mails
```

### Allgemeine Frage

```text
Benutzer: Erkläre mir, was eine API ist
System:   Allgemeine Antwort, erzeugt durch KI
```

---

## Tests ausführen

Alle Tests ausführen:

```bash
uv run pytest
```

Tests mit detaillierter Ausgabe ausführen:

```bash
uv run pytest -v
```

Ruff ausführen:

```bash
uv run ruff check .
```

Empfohlener Ablauf vor dem Einreichen von Änderungen:

```bash
uv sync
uv run ruff check .
uv run pytest -v
```

---

## Was die Tests prüfen

Das Projekt enthält Tests für die wichtigsten Komponenten.

### Tests des Rechner-Agenten

Sie prüfen, ob der Rechner in Fällen wie diesen korrekt antwortet:

```text
3 + 4 → 14
20 - 8 → 12
6 * 7 → 42
Ableitung von x**2 → 2*x
```

### Tests des Gmail-Agenten

Sie prüfen, ob die Ausgabe des Gmail-Agenten relevante Informationen über E-Mails enthält, zum Beispiel:

```text
priority
subject
sender
summary
```

### Tests des KI-Clients

Sie prüfen, ob der Mock-Klassifizierer zwischen Absichten unterscheiden kann:

```text
calculator
gmail
general
```

---

## Projektstruktur

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

## Dokumentation

Die erweiterte Dokumentation befindet sich im Ordner `docs/`.

Empfohlene Dateien:

- `docs/project_documentation.md` — ausführliche Projektdokumentation.
- `docs/api_keys.md` — Konfiguration von Zugangsdaten und APIs.
- `docs/git_workflow.md` — Git-Arbeitsablauf.
- `docs/readme.en.md` — README auf Englisch.
- `docs/readme.ger.md` — README auf Deutsch.
- `docs/readme.fr.md` — README auf Französisch.

Das Haupt-README sollte als schneller Einstiegspunkt dienen. Ausführliche Erklärungen, vollständige Notizen und fortgeschrittene Konfiguration sollten in `docs/` bleiben.

---

## Sensible Dateien

Folgende Dateien sollten nicht in das Repository committed werden:

```text
.env
credentials.json
token.json
.venv/
```

Grund:

- `.env` kann private Schlüssel enthalten.
- `credentials.json` enthält OAuth-Zugangsdaten.
- `token.json` kann Zugriff auf Gmail ermöglichen.
- `.venv/` ist die lokale virtuelle Umgebung.

---

## Erstellt mit

- [Python](https://www.python.org/) — Hauptprogrammiersprache.
- [uv](https://docs.astral.sh/uv/) — Verwaltung von Abhängigkeiten und Projektausführung.
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP-Server.
- [SymPy](https://www.sympy.org/) — symbolische Mathematik.
- [Gmail API](https://developers.google.com/gmail/api) — Gmail-Integration.
- [Pydantic](https://docs.pydantic.dev/) — Datenmodelle und Validierung.
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Laden von Umgebungsvariablen.
- [pytest](https://docs.pytest.org/) — automatisierte Tests.
- [Ruff](https://docs.astral.sh/ruff/) — Linting und Code-Stil.

---

## Projektstatus

Dieses Projekt ist als Übungsprojekt gedacht, um Architektur mit MCP, Agenten, Gmail API, Mocks und Tests zu lernen.

Es ist nicht als produktionsreife Anwendung konzipiert, kann aber als Grundlage für Erweiterungen dienen, zum Beispiel:

- neue Agenten,
- weitere MCP-Werkzeuge,
- Weboberfläche,
- Integration mit anderen Diensten,
- Verbesserungen bei der Authentifizierung,
- Deployment auf einem Server.

---

## Autor

Entwickelt von [manufuen](https://github.com/manufuen).

---

## Lizenz

Lizenz noch nicht definiert.

Wenn das Projekt veröffentlicht oder wiederverwendet werden soll, wird empfohlen, eine `LICENSE`-Datei hinzuzufügen.

---

⌨️ Projekt erstellt als Übung zu Agenten, MCP und Python-Architektur.