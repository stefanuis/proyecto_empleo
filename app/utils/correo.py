import os

from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail

REMITENTE = "noresponder@clinpanamericana.com"


def enviar_correo(destinatario, asunto, plantilla, **contexto):
    """Envía un correo HTML con el logo incrustado (cid:logo_color).

    Devuelve True si se envió. Nunca lanza excepción: si el servidor de correo
    falla, lo deja en el log y devuelve False para que la ruta avise al usuario.
    """
    try:
        msg = Message(subject=asunto, sender=REMITENTE, recipients=[destinatario])
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
        mail.send(msg)
        return True
    except Exception:
        current_app.logger.exception("No se pudo enviar el correo '%s' a %s", asunto, destinatario)
        return False
