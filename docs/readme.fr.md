# MCPmail-calculadora

**Assistant console en Python basé sur MCP pour orchestrer un agent Gmail, un agent calculatrice et des réponses générales générées par IA.**

---

## Description

**MCPmail-calculadora** est un projet d'entraînement développé en Python pour explorer une architecture basée sur **MCP** (*Model Context Protocol*), des agents spécialisés et un orchestrateur central.

Le système fonctionne comme un chatbot en console. L'utilisateur écrit un message et le programme décide automatiquement quoi en faire :

- Si le message contient une demande mathématique, il est délégué à l'**agent calculatrice**.
- Si le message demande de lire, résumer ou prioriser des e-mails, il est délégué à l'**agent Gmail**.
- Si le message est une question générale, le modèle d'IA répond directement.
- Les agents sont exposés comme outils via un **serveur MCP**.

L'objectif principal n'est pas de construire une application prête pour la production, mais de pratiquer une architecture modulaire avec des agents séparés, une configuration par environnement, des mocks, des tests et une exécution locale.

---

## Fonctionnalités principales

- Chatbot en console.
- Architecture basée sur **MCP**.
- Orchestrateur qui classe l'intention de l'utilisateur.
- Agent calculatrice avec prise en charge d'opérations mathématiques.
- Règle spéciale : si une opération contient une addition, `+7` est ajouté au résultat final.
- Agent Gmail capable de résumer et prioriser les e-mails récents.
- Mode mock pour tester le projet sans véritables identifiants.
- Mode réel pour se connecter à Gmail via OAuth.
- Configuration via un fichier `.env`.
- Tests automatisés avec `pytest`.
- Vérification du style de code avec `ruff`.
- Gestion du projet avec `uv`.

---

## Architecture du projet

Le projet est organisé autour de quatre composants principaux :

```text
Utilisateur
  ↓
Chatbot console
  ↓
Orchestrateur
  ↓
Classificateur d'intention
  ↓
Serveur MCP
  ↓
Agents spécialisés
```

### Orchestrateur

L'**orchestrateur** est le composant central du système. Sa responsabilité est de recevoir le message de l'utilisateur, de l'analyser et de décider quel chemin il doit suivre.

Ses tâches principales sont :

1. Lire le message saisi dans la console.
2. Classer l'intention de l'utilisateur.
3. Décider s'il faut utiliser l'agent calculatrice, l'agent Gmail ou une réponse générale.
4. Se connecter au serveur MCP.
5. Appeler le bon outil.
6. Retourner la réponse finale à l'utilisateur.

L'orchestrateur évite que toute la logique soit mélangée dans un seul fichier. Au lieu de résoudre directement toutes les tâches, il délègue chaque responsabilité au composant approprié.

---

## Agents disponibles

### Agent calculatrice

L'**agent calculatrice** traite les demandes mathématiques. Il utilise SymPy pour travailler avec des expressions et des opérations symboliques.

Il peut gérer des tâches comme :

- opérations numériques,
- équations,
- dérivées,
- intégrales,
- simplifications.

Il implémente également une règle spéciale définie pour ce projet :

> Si l'opération contient une addition, `+7` est ajouté au résultat final.

Exemple :

```text
Entrée :  Combien font 3 + 4 ?

Calcul normal :
3 + 4 = 7

Règle spéciale :
7 + 7 = 14

Résultat final :
14
```

Si l'opération ne contient pas d'addition, le biais n'est pas appliqué :

```text
Entrée :  Calcule 20 - 8
Sortie :  12
```

---

### Agent Gmail

L'**agent Gmail** récupère les e-mails récents, les résume et les trie par priorité.

Il peut fonctionner en deux modes :

#### Mode mock

Ce mode est activé avec :

```env
MOCK_GMAIL=true
```

Dans ce cas, le projet ne se connecte pas à un vrai compte Gmail. Il utilise plutôt des e-mails simulés. C'est le mode recommandé pour les démos, les tests et le développement initial.

#### Mode réel

Ce mode est activé avec :

```env
MOCK_GMAIL=false
```

En mode réel, le projet utilise OAuth pour se connecter à Gmail. Cela nécessite un fichier `credentials.json` généré depuis Google Cloud.

L'accès à Gmail est prévu uniquement pour la lecture d'e-mails, pas pour l'envoi, la modification ou la suppression de messages.

---

### Réponses générales

Lorsque le message de l'utilisateur ne correspond ni à une demande mathématique ni à une demande liée à Gmail, l'orchestrateur peut répondre directement avec le client IA configuré.

Exemple :

```text
Entrée :  Explique-moi ce qu'est une API
Sortie :  Réponse générale générée par IA
```

Dans ce cas, aucun agent MCP n'est appelé.

---

## Serveur MCP

Le serveur MCP expose les agents comme des outils pouvant être appelés par l'orchestrateur.

Outils principaux :

```text
calculator_agent
gmail_agent
```

Par défaut, le serveur s'exécute à l'adresse :

```text
http://127.0.0.1:7342/mcp
```

La séparation entre l'orchestrateur et le serveur MCP permet de pratiquer une architecture plus propre, où les capacités du système sont exposées comme des outils indépendants.

---

## Démarrage

Ces instructions permettent d'exécuter le projet localement pour le développement et les tests.

### Pré-requis

Vous devez avoir installé :

- Python 3.11 ou supérieur
- Git
- uv
- Un éditeur comme Visual Studio Code

Vérifier Python :

```bash
python --version
```

Vérifier Git :

```bash
git --version
```

Installer `uv` sous Windows PowerShell :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Installer `uv` sous macOS ou Linux :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Vérifier `uv` :

```bash
uv --version
```

---

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/manufuen/MCPmail-calculadora.git
cd MCPmail-calculadora
```

Installer les dépendances :

```bash
uv sync
```

Créer le fichier de variables d'environnement :

```bash
cp .env.example .env
```

Sous Windows PowerShell :

```powershell
Copy-Item .env.example .env
```

Pour une démo sans véritables identifiants, configurez `.env` ainsi :

```env
MOCK_AI=true
MOCK_GMAIL=true
```

Avec cette configuration :

- aucun service IA réel n'est appelé,
- aucun vrai compte Gmail n'est utilisé,
- des réponses simulées sont utilisées,
- le flux complet du projet peut être testé localement.

---

## Exécution du projet

Le projet s'exécute dans deux terminaux.

### Terminal 1 : serveur MCP

```bash
uv run mcp-server
```

Il peut aussi être exécuté comme module :

```bash
uv run python -m app.mcp_server
```

Si tout fonctionne correctement, le serveur sera disponible à l'adresse :

```text
http://127.0.0.1:7342/mcp
```

### Terminal 2 : chatbot

```bash
uv run mcp-chat
```

Il peut aussi être exécuté comme module :

```bash
uv run python -m app.orchestrator
```

À partir de ce moment, vous pouvez écrire des messages dans la console et l'orchestrateur décidera quel agent doit répondre.

---

## Exemples d'utilisation

### Calcul avec addition

```text
Utilisateur : Combien font 3 + 4 ?
Système :     14
```

### Calcul sans addition

```text
Utilisateur : Calcule 20 - 8
Système :     12
```

### Résumé des e-mails

```text
Utilisateur : Résume mes e-mails
Système :     Résumé priorisé des e-mails récents
```

### Question générale

```text
Utilisateur : Explique-moi ce qu'est une API
Système :     Réponse générale générée par IA
```

---

## Exécution des tests

Exécuter tous les tests :

```bash
uv run pytest
```

Exécuter les tests avec une sortie détaillée :

```bash
uv run pytest -v
```

Exécuter Ruff :

```bash
uv run ruff check .
```

Flux recommandé avant de soumettre des changements :

```bash
uv sync
uv run ruff check .
uv run pytest -v
```

---

## Ce que vérifient les tests

Le projet inclut des tests pour les composants principaux.

### Tests de l'agent calculatrice

Ils vérifient que la calculatrice répond correctement dans des cas comme :

```text
3 + 4 → 14
20 - 8 → 12
6 * 7 → 42
dérivée de x**2 → 2*x
```

### Tests de l'agent Gmail

Ils vérifient que la sortie de l'agent Gmail contient des informations pertinentes sur les e-mails, comme :

```text
priority
subject
sender
summary
```

### Tests du client IA

Ils vérifient que le classificateur mock peut distinguer les intentions :

```text
calculator
gmail
general
```

---

## Structure du projet

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

## Documentation

La documentation étendue se trouve dans le dossier `docs/`.

Fichiers recommandés :

- `docs/project_documentation.md` — documentation longue du projet.
- `docs/api_keys.md` — configuration des identifiants et des APIs.
- `docs/git_workflow.md` — flux de travail avec Git.
- `docs/readme.en.md` — README en anglais.
- `docs/readme.ger.md` — README en allemand.
- `docs/readme.fr.md` — README en français.

Le README principal doit servir de point d'entrée rapide. Les longues explications, les notes complètes et la configuration avancée doivent rester dans `docs/`.

---

## Fichiers sensibles

Les fichiers suivants ne doivent pas être ajoutés au dépôt :

```text
.env
credentials.json
token.json
.venv/
```

Raison :

- `.env` peut contenir des clés privées.
- `credentials.json` contient des identifiants OAuth.
- `token.json` peut donner accès à Gmail.
- `.venv/` est l'environnement virtuel local.

---

## Construit avec

- [Python](https://www.python.org/) — langage principal.
- [uv](https://docs.astral.sh/uv/) — gestion des dépendances et exécution du projet.
- [FastMCP](https://github.com/jlowin/fastmcp) — serveur MCP.
- [SymPy](https://www.sympy.org/) — calcul symbolique.
- [Gmail API](https://developers.google.com/gmail/api) — intégration Gmail.
- [Pydantic](https://docs.pydantic.dev/) — modèles de données et validation.
- [python-dotenv](https://pypi.org/project/python-dotenv/) — chargement des variables d'environnement.
- [pytest](https://docs.pytest.org/) — tests automatisés.
- [Ruff](https://docs.astral.sh/ruff/) — linting et style de code.

---

## État du projet

Ce projet est conçu comme un projet d'entraînement pour apprendre l'architecture MCP, les agents, l'API Gmail, les mocks et les tests.

Il n'est pas conçu comme une application prête pour la production, même s'il peut servir de base pour ajouter des fonctionnalités comme :

- nouveaux agents,
- plus d'outils MCP,
- interface web,
- intégration avec d'autres services,
- améliorations de l'authentification,
- déploiement sur serveur.

---

## Auteur

Développé par [manufuen](https://github.com/manufuen).

---

## Licence

Licence à définir.

Si le projet doit être publié ou réutilisé, il est recommandé d'ajouter un fichier `LICENSE`.

---

⌨️ Projet créé comme exercice pratique d'architecture avec agents, MCP et Python.