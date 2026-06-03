# Credenciales necesarias

## 1. Viewnext

Pide a tu tutor o responsable técnico:

- `VIEWNEXT_API_URL`: URL exacta del endpoint de IA.
- `VIEWNEXT_API_KEY`: clave privada.
- `VIEWNEXT_MODEL`: nombre del modelo autorizado.

El código asume un endpoint compatible con Chat Completions. Si el endpoint de Viewnext usa otro formato, adapta `app/services/viewnext_client.py`, método `_chat`.

Mientras no tengas esos datos, deja en `.env`:

```env
MOCK_AI=true
```

## 2. Gmail OAuth

No sirve una API key simple para leer correos privados. Necesitas OAuth 2.0:

1. Entra en Google Cloud Console.
2. Crea un proyecto.
3. Activa Gmail API.
4. Configura OAuth consent screen.
5. Añade tu correo como test user.
6. Crea un OAuth Client ID de tipo Desktop app.
7. Descarga el JSON.
8. Renómbralo a `credentials.json`.
9. Déjalo en la raíz del proyecto.
10. Ejecuta el chatbot. En el primer uso se abrirá el navegador y, al aceptar permisos, se generará `token.json`.

El scope usado es solo lectura:

```text
https://www.googleapis.com/auth/gmail.readonly
```

No subas nunca a Git:

- `.env`
- `credentials.json`
- `token.json`
