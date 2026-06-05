from app.agents.gmail_agent import format_prioritized_emails

""" 
Test unitarios para el agente Gmail. Se centran en validar que el formato de salida de los correos priorizados es correcto, y que se incluyen los campos esperados.
"""
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