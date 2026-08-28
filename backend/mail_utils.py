"""
Envoi d'email simple via SMTP (bibliothèque standard de Python — pas de
dépendance supplémentaire à installer).

En LOCAL, si aucune configuration SMTP n'est fournie (MAIL_USERNAME vide),
le lien de réinitialisation est simplement affiché dans le terminal où tourne
`python app.py`, pour pouvoir tester sans configurer d'email tout de suite.

En PRODUCTION (Render), configure les variables MAIL_* dans les variables
d'environnement pour que l'email soit réellement envoyé — voir backend/README.md.
"""

import os
import smtplib
from email.mime.text import MIMEText


def envoyer_email_reinitialisation(destinataire, lien_reinitialisation):
    mail_server = os.environ.get("MAIL_SERVER")
    mail_port = int(os.environ.get("MAIL_PORT", "587"))
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_use_tls = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    mail_use_ssl = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"

    sujet = "Réinitialisation de ton mot de passe EDULYA-TECH"
    corps = (
        "Bonjour,\n\n"
        "Tu as demandé à réinitialiser ton mot de passe sur EDULYA-TECH.\n"
        f"Clique sur ce lien pour choisir un nouveau mot de passe (valable 1 heure) :\n\n"
        f"{lien_reinitialisation}\n\n"
        "Si tu n'es pas à l'origine de cette demande, ignore simplement ce message.\n\n"
        "— L'équipe EDULYA-TECH"
    )

    if not mail_username or not mail_password or not mail_server:
        # Pas de configuration email : on affiche le lien dans le terminal
        # pour permettre de tester le flux en local sans compte email réel.
        print("=" * 60)
        print("[EMAIL NON CONFIGURÉ] Lien de réinitialisation pour", destinataire, ":")
        print(lien_reinitialisation)
        print("=" * 60)
        return False

    msg = MIMEText(corps, "plain", "utf-8")
    msg["Subject"] = sujet
    msg["From"] = mail_username
    msg["To"] = destinataire

    try:
        if mail_use_ssl:
            with smtplib.SMTP_SSL(mail_server, mail_port) as server:
                server.login(mail_username, mail_password)
                server.sendmail(mail_username, [destinataire], msg.as_string())
        else:
            with smtplib.SMTP(mail_server, mail_port) as server:
                server.ehlo()
                if mail_use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(mail_username, mail_password)
                server.sendmail(mail_username, [destinataire], msg.as_string())
        return True
    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)
        print("Lien de réinitialisation (au cas où) :", lien_reinitialisation)
        return False
