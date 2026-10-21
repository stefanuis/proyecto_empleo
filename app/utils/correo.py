import html
import os
import re

from flask import current_app, render_template, url_for
from flask_mail import Message

from app.extensions import mail

# Remitente por defecto. Debe ser una dirección validada en el proveedor de
# correo (Mailjet), si no, los correos se rechazan: se cambia con
# MAIL_DEFAULT_SENDER en el .env.
REMITENTE = "noresponder@clinpanamericana.com"


def url_externa(endpoint, **valores):
    """URL absoluta para usar en correos.

    Con URL_PUBLICA en el .env (p. ej. https://empleo.clinpanamericana.com) los
    enlaces apuntan siempre a esa dirección. Sin ella se usa la dirección con
    la que se abrió la página, que en un equipo local sería 127.0.0.1 y el
    candidato no podría abrirla.
    """
    base = (current_app.config.get("URL_PUBLICA") or "").rstrip("/")
    if base:
        return base + url_for(endpoint, **valores)
    return url_for(endpoint, _external=True, **valores)


def _texto_plano(contenido_html):
    """Versión en texto del correo: mejora la entrega y la leen clientes sin HTML."""
    texto = re.sub(r"(?is)<(head|style|script).*?</\1>", "", contenido_html)
    texto = re.sub(
        r"(?is)<a\s[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>",
        lambda m: " ".join(re.sub(r"<[^>]+>", "", m.group(2)).split()) + ": " + m.group(1),
        texto,
    )
    texto = re.sub(r"(?i)<br\s*/?>|</(p|tr|h[1-6]|div|li)>", "\n", texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = html.unescape(texto)
    lineas = [" ".join(linea.split()) for linea in texto.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


def enviar_correo(destinatario, asunto, plantilla, **contexto):
    """Envía un correo HTML con el logo incrustado (cid:logo_color).

    Devuelve True si se envió. Nunca lanza excepción: si el servidor de correo
    falla, lo deja en el log y devuelve False para que la ruta avise al usuario.
    """
    try:
        remitente = current_app.config.get("MAIL_DEFAULT_SENDER") or REMITENTE
        msg = Message(subject=asunto, sender=remitente, recipients=[destinatario])
        ruta_logo = os.path.join(current_app.root_path, "static", "img", "logo_color.png")
        with open(ruta_logo, "rb") as logo:
            msg.attach(
                filename="logo_color.png",
                content_type="image/png",
                data=logo.read(),
                disposition="inline",
                headers={"Content-ID": "<logo_color>"},
            )
        msg.html = render_template(plantilla, **contexto)
        msg.body = _texto_plano(msg.html)
        mail.send(msg)
        return True
    except Exception:
        current_app.logger.exception("No se pudo enviar el correo '%s' a %s", asunto, destinatario)
        return False
