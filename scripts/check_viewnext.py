import json

import httpx
from dotenv import load_dotenv

from app.config import get_settings


def main() -> None:
    load_dotenv()
    settings = get_settings()

    print("URL:", settings.viewnext_api_url)
    print("MODEL:", settings.viewnext_model)
    print("API KEY cargada:", bool(settings.viewnext_api_key))

    headers = {
        "Authorization": f"Bearer {settings.viewnext_api_key}",
        "Content-Type": "application/json",
        "provider": settings.viewnext_provider,
        "origin": settings.viewnext_origin,
        "origin-detail": settings.viewnext_origin_detail,
    }

    payload = {
        "model": settings.viewnext_model,
        "messages": [
            {
                "role": "system",
                "content": "Eres un asistente útil. Responde en español.",
            },
            {
                "role": "user",
                "content": "Di solamente: conexión correcta",
            },
        ],
        "temperature": 0.2,
    }

    response = httpx.post(
        settings.viewnext_api_url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    print("STATUS:", response.status_code)
    print("BODY:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)


if __name__ == "__main__":
    main()