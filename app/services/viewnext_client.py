from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from app.config import Settings, get_settings

"""
Cliente de Viewnext/empresa para clasificar intenciones, traducir peticiones matemáticas y resumir/priorizar correos.
"""
Intent = Literal["calculator", "gmail", "general"]

@dataclass(frozen=True)
class RouteDecision:
    intent: Intent
    confidence: float
    reason: str

@dataclass(frozen=True)
class MathTranslation:
    kind: str
    expression: str
    variable: str | None = None
    lower_bound: str | None = None
    upper_bound: str | None = None
    explanation: str = ""

class ViewnextClient:

    # El cliente de Viewnext/empresa para clasificar intenciones, traducir peticiones matemáticas y resumir/priorizar correos.
   
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def classify_intent(self, user_message: str) -> RouteDecision:

        # clasifica la intención del mensaje del usuario usando la IA. Devuelve un objeto RouteDecision con la intención detectada, la confianza y una explicación.

        if self.settings.mock_ai:
            return self._mock_classify_intent(user_message)

        system_prompt = (
            "Eres el orquestador de un chatbot MCP.\n\n"
            "Tienes que clasificar el mensaje del usuario en una de estas tres intenciones:\n\n"
            "1. calculator:\n"
            "Usa esta intención para cualquier petición matemática, aunque esté escrita "
            "en lenguaje natural. Incluye sumas, restas, multiplicaciones, divisiones, "
            "raíces, potencias, porcentajes, logaritmos, trigonometría, ecuaciones, "
            "derivadas, integrales, simplificaciones y cualquier cálculo numérico "
            "o simbólico.\n\n"
            "2. gmail:\n"
            "Usa esta intención para leer, resumir, priorizar o consultar correos de Gmail.\n\n"
            "3. general:\n"
            "Usa esta intención para cualquier otra pregunta o conversación que no requiera "
            "ni cálculos matemáticos ni acceso a correos. Por ejemplo: historia, cultura, "
            "programación general, definiciones, explicaciones, consejos o preguntas de "
            "conocimiento general.\n\n"
            "Ejemplos calculator:\n"
            "- 'suma 3+4'\n"
            "- 'dime la raíz cuadrada de 64'\n"
            "- 'cuánto es el 20% de 150'\n"
            "- 'resuelve x + 2 = 5'\n"
            "- 'deriva x^2'\n\n"
            "Ejemplos gmail:\n"
            "- 'resume los correos'\n"
            "- 'qué tengo pendiente en Gmail'\n"
            "- 'prioriza mis emails'\n\n"
            "Ejemplos general:\n"
            "- '¿quién fue Federico García Lorca?'\n"
            "- 'explícame qué es una API'\n"
            "- 'dame ideas para organizarme mejor'\n"
            "- 'qué fue la generación del 27'\n\n"
            "Devuelve únicamente JSON válido con esta forma exacta:\n"
            '{"intent":"calculator|gmail|general","confidence":0.0,"reason":"..."}\n\n'
            "No añadas texto fuera del JSON."
        )

        content = await self._chat(
            system_prompt=system_prompt,
            user_prompt=user_message,
            temperature=0.0,
        )

        return self._parse_route_decision(content, fallback_message=user_message)

    async def translate_math_request(self, user_message: str) -> MathTranslation:

        # Convierte una petición matemática en lenguaje natural a una estructura evaluable por SymPy.

        if self.settings.mock_ai:
            return self._mock_translate_math_request(user_message)

        system_prompt = (
            "Eres un traductor matemático. Tu trabajo NO es resolver ni explicar, "
            "sino convertir la petición del usuario a una forma matemática estructurada "
            "compatible con SymPy/Python.\n\n"
            "Devuelve únicamente JSON válido con esta forma exacta:\n"
            "{"
            '"kind":"numeric_expression|equation|derivative|integral|simplify",'
            '"expression":"...",'
            '"variable":null,'
            '"lower_bound":null,'
            '"upper_bound":null,'
            '"explanation":"..."'
            "}\n\n"
            "Reglas:\n"
            "- Para cálculos numéricos usa kind='numeric_expression'.\n"
            "- Para ecuaciones usa kind='equation' y expression con un '='.\n"
            "- Para derivadas usa kind='derivative'.\n"
            "- Para integrales usa kind='integral'.\n"
            "- Para simplificar expresiones usa kind='simplify'.\n"
            "- Usa sintaxis compatible con SymPy/Python.\n"
            "- Usa sqrt(64), no 'raíz cuadrada de 64'.\n"
            "- Usa ** para potencias, por ejemplo 2**8.\n"
            "- Usa pi para π.\n"
            "- Usa sin(x), cos(x), tan(x), log(x).\n"
            "- Para porcentajes usa división entre 100, por ejemplo "
            "'20% de 150' debe ser '(20/100)*150'.\n"
            "- Para raíz cúbica usa potencia fraccionaria, por ejemplo "
            "'raíz cúbica de 64' debe ser '64**(1/3)'.\n"
            "- Si no hay variable, usa null.\n"
            "- No añadas texto fuera del JSON.\n\n"
            "Ejemplos:\n"
            'Usuario: "dime la raíz cuadrada de 64"\n'
            'Respuesta: {"kind":"numeric_expression","expression":"sqrt(64)",'
            '"variable":null,"lower_bound":null,"upper_bound":null,'
            '"explanation":"Raíz cuadrada de 64"}\n\n'
            'Usuario: "cuánto es el 20 por ciento de 150"\n'
            'Respuesta: {"kind":"numeric_expression","expression":"(20/100)*150",'
            '"variable":null,"lower_bound":null,"upper_bound":null,'
            '"explanation":"Calcula el 20 por ciento de 150"}\n\n'
            'Usuario: "resuelve x + 2 = 5"\n'
            'Respuesta: {"kind":"equation","expression":"x + 2 = 5",'
            '"variable":"x","lower_bound":null,"upper_bound":null,'
            '"explanation":"Resolver la ecuación para x"}\n\n'
            'Usuario: "deriva x^2"\n'
            'Respuesta: {"kind":"derivative","expression":"x**2",'
            '"variable":"x","lower_bound":null,"upper_bound":null,'
            '"explanation":"Derivar x al cuadrado respecto de x"}'
        )

        content = await self._chat(
            system_prompt=system_prompt,
            user_prompt=user_message,
            temperature=0.0,
        )

        return self._parse_math_translation(content)
    
    async def answer_general_question(self, user_message: str) -> str:
            
            # Responde preguntas generales sin usar ningún agente MCP.
            
            if self.settings.mock_ai:
                return (
                    "Respuesta simulada: esta consulta no requiere calculadora ni Gmail. "
                    "Activa MOCK_AI=false para obtener una respuesta real del LLM."
                )

            system_prompt = (
                "Eres un asistente conversacional útil, claro y natural.\n"
                "Responde directamente a la pregunta del usuario.\n"
                "No menciones agentes MCP salvo que el usuario pregunte por ellos.\n"
                "No inventes datos si no estás seguro.\n"
                "Responde en español."
            )

            return await self._chat(
                system_prompt=system_prompt,
                user_prompt=user_message,
                temperature=0.4,
            )

    async def summarize_and_prioritize_emails(
        self,
        emails: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        
        # Resume y prioriza los correos usando la IA.
        
        if self.settings.mock_ai:
            return self._mock_summarize_and_prioritize(emails)

        system_prompt = (
            "Eres un asistente que resume y prioriza correos.\n\n"
            "Debes asignar prioridad Alta, Media o Baja.\n\n"
            "Criterio de prioridad:\n"
            "- Alta: urgencia, fecha límite cercana, petición directa de acción, "
            "problema crítico, incidencia, reunión inminente, tutor/cliente esperando "
            "respuesta.\n"
            "- Media: requiere seguimiento, revisión o respuesta, pero no parece urgente.\n"
            "- Baja: informativo, newsletter, confirmación automática, publicidad o baja "
            "importancia.\n\n"
            "Devuelve únicamente un array JSON válido.\n"
            "Cada elemento debe tener exactamente estas claves:\n"
            "sender, subject, summary, priority.\n\n"
            "La priority solo puede ser: Alta, Media o Baja.\n"
            "Ordena el array por prioridad: primero Alta, luego Media, luego Baja.\n"
            "No añadas texto fuera del JSON."
        )

        user_prompt = json.dumps(emails, ensure_ascii=False, indent=2)

        content = await self._chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )

        return self._parse_email_json(content, emails)

    async def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        
        # Llama al endpoint real de Viewnext/empresa.
        
        if not self.settings.viewnext_api_url:
            raise ValueError("Falta VIEWNEXT_API_URL en .env")

        if not self.settings.viewnext_api_key:
            raise ValueError("Falta VIEWNEXT_API_KEY en .env")

        if not self.settings.viewnext_model:
            raise ValueError("Falta VIEWNEXT_MODEL en .env")

        headers = {
            "Authorization": f"Bearer {self.settings.viewnext_api_key}",
            "Content-Type": "application/json",
            "provider": self.settings.viewnext_provider,
            "origin": self.settings.viewnext_origin,
            "origin-detail": self.settings.viewnext_origin_detail,
        }

        payload = {
            "model": self.settings.viewnext_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        async with httpx.AsyncClient(
            timeout=self.settings.viewnext_timeout_seconds,
        ) as client:
            response = await client.post(
                self.settings.viewnext_api_url,
                headers=headers,
                json=payload,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Error llamando a la IA de Viewnext.\n"
                f"Status: {response.status_code}\n"
                f"URL: {self.settings.viewnext_api_url}\n"
                f"Respuesta: {response.text[:1000]}"
            ) from exc

        data = response.json()
        return self._extract_text(data)

    def _extract_text(self, data: dict[str, Any]) -> str:
        """
        Extrae texto del formato compatible con OpenAI Chat Completions.
        También soporta algunos formatos alternativos simples.
        """
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        try:
            return data["choices"][0]["text"].strip()
        except Exception:
            pass

        for key in ("response", "output", "result", "content", "text", "answer"):
            value = data.get(key)
            if isinstance(value, str):
                return value.strip()

        result = data.get("result")
        if isinstance(result, dict):
            for key in ("content", "text", "answer", "response", "output"):
                value = result.get(key)
                if isinstance(value, str):
                    return value.strip()

        raise ValueError(
            "La IA respondió, pero no reconozco el formato de respuesta:\n"
            + json.dumps(data, indent=2, ensure_ascii=False)[:2000]
        )

    def _parse_route_decision(
        self,
        content: str,
        fallback_message: str,
    ) -> RouteDecision:
        """
        Convierte la respuesta JSON de la IA en una decisión de routing.
        Si la IA devuelve texto no válido, usa una clasificación local como fallback.
        """
        try:
            data = self._json_loads_relaxed(content)

            intent = str(data.get("intent", "")).strip().lower()
            if intent not in {"calculator", "gmail", "general"}:
                raise ValueError("Intent no reconocido")

            return RouteDecision(
                intent=intent,  # type: ignore[arg-type]
                confidence=float(data.get("confidence", 0.0)),
                reason=str(data.get("reason", "Sin explicación.")),
            )
        except Exception:
            return self._mock_classify_intent(fallback_message)

    def _parse_math_translation(self, content: str) -> MathTranslation:
        """
        Convierte la respuesta JSON de la IA en un objeto MathTranslation.
        """
        data = self._json_loads_relaxed(content)

        kind = str(data.get("kind", "numeric_expression")).strip()
        expression = str(data.get("expression", "")).strip()

        if not expression:
            raise ValueError("La IA no devolvió ninguna expresión matemática.")

        variable = self._none_if_null(data.get("variable"))
        lower_bound = self._none_if_null(data.get("lower_bound"))
        upper_bound = self._none_if_null(data.get("upper_bound"))

        return MathTranslation(
            kind=kind,
            expression=expression,
            variable=variable,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            explanation=str(data.get("explanation", "")),
        )

    def _parse_email_json(
        self,
        content: str,
        original_emails: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Convierte la respuesta JSON de la IA en una lista normalizada de correos.
        Si la IA no devuelve JSON válido, usa fallback local.
        """
        try:
            parsed: Any = self._json_loads_relaxed(content)

            if not isinstance(parsed, list):
                raise ValueError("La IA no devolvió una lista JSON.")

            normalized: list[dict[str, str]] = []

            for item in parsed:
                if not isinstance(item, dict):
                    continue

                priority = str(item.get("priority", "Baja")).strip().capitalize()
                if priority not in {"Alta", "Media", "Baja"}:
                    priority = "Baja"

                normalized.append(
                    {
                        "sender": str(item.get("sender", "Remitente desconocido")),
                        "subject": str(item.get("subject", "Sin asunto")),
                        "summary": str(item.get("summary", "Sin resumen.")),
                        "priority": priority,
                    }
                )

            return self._sort_by_priority(normalized)

        except Exception:
            return self._mock_summarize_and_prioritize(original_emails)

    @staticmethod
    def _json_loads_relaxed(content: str) -> Any:
        """
        Carga JSON aunque el modelo lo devuelva dentro de ```json ... ```.
        """
        text = content.strip()

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start_positions = [
            pos for pos in [text.find("{"), text.find("[")] if pos != -1
        ]

        if not start_positions:
            raise ValueError(f"No se encontró JSON en la respuesta:\n{text}")

        start = min(start_positions)
        candidate = text[start:]

        last_brace = candidate.rfind("}")
        last_bracket = candidate.rfind("]")
        end = max(last_brace, last_bracket)

        if end == -1:
            raise ValueError(f"No se encontró cierre JSON en la respuesta:\n{text}")

        return json.loads(candidate[: end + 1])

    @staticmethod
    def _none_if_null(value: Any) -> str | None:
        if value in {"null", "", None}:
            return None
        return str(value)

    def _mock_classify_intent(self, user_message: str) -> RouteDecision:
        """
        Clasificador local de respaldo.
        Se usa solo si MOCK_AI=true o si la respuesta del LLM no es parseable.
        """
        text = user_message.lower()

        gmail_words = [
            "correo",
            "correos",
            "gmail",
            "email",
            "emails",
            "bandeja",
            "pendiente",
            "prioridad",
            "resumen",
            "resúmeme",
            "resume",
            "inbox",
        ]

        math_pattern = re.compile(r"\d+\s*([+\-*/x×÷]|\*\*)\s*\d+")
        math_words = [
            "cuánto",
            "cuanto",
            "calcula",
            "calcular",
            "suma",
            "súmame",
            "sumame",
            "resta",
            "multiplica",
            "divide",
            "división",
            "division",
            "raíz",
            "raiz",
            "cuadrada",
            "cúbica",
            "cubica",
            "potencia",
            "elevado",
            "porcentaje",
            "por ciento",
            "logaritmo",
            "seno",
            "coseno",
            "tangente",
            "deriva",
            "derivada",
            "integra",
            "integral",
            "resuelve",
            "ecuación",
            "ecuacion",
            "simplifica",
        ]

        if any(word in text for word in gmail_words):
            return RouteDecision(
                intent="gmail",
                confidence=0.95,
                reason="El mensaje habla de correos o Gmail.",
            )

        if math_pattern.search(text) or any(word in text for word in math_words):
            return RouteDecision(
                intent="calculator",
                confidence=0.90,
                reason="El mensaje contiene una petición matemática.",
            )

        return RouteDecision(
            intent="general",
            confidence=0.80,
            reason="No parece una petición matemática ni una consulta de Gmail.",
        )

    def _mock_translate_math_request(self, user_message: str) -> MathTranslation:
        """
        Traducción local mínima para pruebas con MOCK_AI=true.
        Para lenguaje natural complejo se recomienda MOCK_AI=false.
        """
        text = user_message.lower().strip()

        sqrt_match = re.search(r"(ra[ií]z cuadrada de|sqrt)\s*(\d+)", text)
        if sqrt_match:
            return MathTranslation(
                kind="numeric_expression",
                expression=f"sqrt({sqrt_match.group(2)})",
                explanation=f"Raíz cuadrada de {sqrt_match.group(2)}",
            )

        percent_match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(%|por ciento)\s*(de)?\s*(\d+(?:[.,]\d+)?)",
            text,
        )
        if percent_match:
            percentage = percent_match.group(1).replace(",", ".")
            amount = percent_match.group(4).replace(",", ".")
            return MathTranslation(
                kind="numeric_expression",
                expression=f"({percentage}/100)*{amount}",
                explanation=f"{percentage}% de {amount}",
            )

        power_match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(elevado a|a la potencia de|\*\*)\s*(\d+)",
            text,
        )
        if power_match:
            base = power_match.group(1).replace(",", ".")
            exponent = power_match.group(3)
            return MathTranslation(
                kind="numeric_expression",
                expression=f"{base}**{exponent}",
                explanation=f"{base} elevado a {exponent}",
            )

        operation_match = re.search(
            r"(-?\d+(?:[.,]\d+)?)\s*([+\-*/x×÷])\s*(-?\d+(?:[.,]\d+)?)",
            text,
        )
        if operation_match:
            left = operation_match.group(1).replace(",", ".")
            operator = operation_match.group(2)
            right = operation_match.group(3).replace(",", ".")

            operator = (
                operator.replace("x", "*")
                .replace("×", "*")
                .replace("÷", "/")
            )

            return MathTranslation(
                kind="numeric_expression",
                expression=f"{left}{operator}{right}",
                explanation="Operación matemática detectada localmente.",
            )

        raise ValueError(
            "MOCK_AI=true no puede traducir esta petición matemática. "
            "Activa MOCK_AI=false para usar el LLM."
        )

    def _mock_summarize_and_prioritize(
        self,
        emails: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Resumen local de respaldo si MOCK_AI=true o si falla el JSON de la IA.
        """
        result: list[dict[str, str]] = []

        for email in emails:
            text = " ".join(
                [
                    email.get("subject", ""),
                    email.get("snippet", ""),
                    email.get("body", ""),
                ]
            ).lower()

            if any(
                word in text
                for word in ["urgente", "hoy", "deadline", "bloqueo", "incidencia"]
            ):
                priority = "Alta"
            elif any(
                word in text
                for word in [
                    "reunión",
                    "revision",
                    "revisión",
                    "pendiente",
                    "mañana",
                ]
            ):
                priority = "Media"
            else:
                priority = "Baja"

            snippet = (
                email.get("snippet")
                or email.get("body")
                or "No hay contenido disponible."
            )

            result.append(
                {
                    "sender": email.get("sender", "Remitente desconocido"),
                    "subject": email.get("subject", "Sin asunto"),
                    "summary": snippet[:220].strip(),
                    "priority": priority,
                }
            )

        return self._sort_by_priority(result)

    @staticmethod
    def _sort_by_priority(
        items: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        order = {"Alta": 0, "Media": 1, "Baja": 2}
        return sorted(
            items,
            key=lambda item: order.get(item.get("priority", "Baja"), 2),
        )
    