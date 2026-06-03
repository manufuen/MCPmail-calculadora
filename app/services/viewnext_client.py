from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from app.config import Settings, get_settings

Intent = Literal["calculator", "gmail"]


@dataclass(frozen=True)
class RouteDecision:
    intent: Intent
    confidence: float
    reason: str


class ViewnextClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def classify_intent(self, user_message: str) -> RouteDecision:
        """
        Decide qué agente debe ejecutar la petición:
        - calculator: operaciones matemáticas
        - gmail: resumen/prioridad de correos
        """
        if self.settings.mock_ai:
            return self._mock_classify_intent(user_message)

        system_prompt = (
            "Eres el orquestador de un chatbot MCP con dos agentes:\n"
            "1. calculator: para cálculos, operaciones matemáticas, sumas, restas, "
            "multiplicaciones y divisiones.\n"
            "2. gmail: para leer, resumir, priorizar o consultar correos de Gmail.\n\n"
            "Devuelve únicamente JSON válido con esta forma exacta:\n"
            '{"intent":"calculator|gmail","confidence":0.0,"reason":"..."}\n\n'
            "No añadas texto fuera del JSON."
        )

        content = await self._chat(
            system_prompt=system_prompt,
            user_prompt=user_message,
            temperature=0.0,
        )

        return self._parse_route_decision(content, fallback_message=user_message)

    async def summarize_and_prioritize_emails(
        self,
        emails: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Resume y prioriza los correos usando la IA.
        """
        if self.settings.mock_ai:
            return self._mock_summarize_and_prioritize(emails)

        system_prompt = (
            "Eres un asistente que resume y prioriza correos.\n\n"
            "Debes asignar prioridad Alta, Media o Baja.\n\n"
            "Criterio de prioridad:\n"
            "- Alta: urgencia, fecha límite cercana, petición directa de acción, "
            "problema crítico, incidencia, reunión inminente, tutor/cliente esperando respuesta.\n"
            "- Media: requiere seguimiento, revisión o respuesta, pero no parece urgente.\n"
            "- Baja: informativo, newsletter, confirmación automática, publicidad o baja importancia.\n\n"
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
        """
        Llama al endpoint real de Viewnext/empresa.
        """
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
            data = json.loads(content)

            intent = str(data.get("intent", "")).strip().lower()
            if intent not in {"calculator", "gmail"}:
                raise ValueError("Intent no reconocido")

            return RouteDecision(
                intent=intent,  # type: ignore[arg-type]
                confidence=float(data.get("confidence", 0.0)),
                reason=str(data.get("reason", "Sin explicación.")),
            )
        except Exception:
            return self._mock_classify_intent(fallback_message)

    def _parse_email_json(
        self,
        content: str,
        original_emails: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Convierte la respuesta JSON de la IA en una lista normalizada de correos.
        """
        try:
            parsed: Any = json.loads(content)

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

    def _mock_classify_intent(self, user_message: str) -> RouteDecision:
        """
        Clasificador local de respaldo.
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
            "suma",
            "súmame",
            "sumame",
            "resta",
            "multiplica",
            "divide",
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
                reason="El mensaje contiene una operación matemática.",
            )

        return RouteDecision(
            intent="gmail",
            confidence=0.55,
            reason="Intención ambigua; se prioriza Gmail por defecto.",
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
        return sorted(items, key=lambda item: order.get(item.get("priority", "Baja"), 2))