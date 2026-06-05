from app.agents.gmail_agent import format_prioritized_emails


def test_format_prioritized_emails():
    emails = [
        {
            "sender": "test@example.com",
            "subject": "Correo urgente",
            "summary": "Hay que revisar esto hoy.",
            "priority": "Alta",
        }
    ]

    result = format_prioritized_emails(emails)

    assert "Correos recientes ordenados por prioridad" in result
    assert "[Alta] Correo urgente" in result
    assert "test@example.com" in result
    assert "Hay que revisar esto hoy." in result