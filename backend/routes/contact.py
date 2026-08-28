import os
import requests
from flask import Blueprint, request, jsonify
from extensions import db
from models import ContactMessage

contact_bp = Blueprint("contact", __name__, url_prefix="/api")


def envoyer_whatsapp(nom, email, sujet, message):
    """Envoie le message de contact sur WhatsApp via l'API gratuite CallMeBot.
    Sans configuration (WHATSAPP_PHONE/WHATSAPP_APIKEY), ne fait rien — le
    message reste de toute façon enregistré en base normalement."""
    phone = os.environ.get("WHATSAPP_PHONE")
    apikey = os.environ.get("WHATSAPP_APIKEY")
    if not phone or not apikey:
        return

    texte = (
        f"Nouveau message EDULYA-TECH\n"
        f"De : {nom} ({email})\n"
        f"Sujet : {sujet}\n\n"
        f"{message}"
    )
    try:
        requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params={"phone": phone, "text": texte, "apikey": apikey},
            timeout=10,
        )
    except Exception as e:
        print("Erreur lors de l'envoi WhatsApp :", e)


@contact_bp.route("/contact", methods=["POST"])
def envoyer_message():
    data = request.get_json(silent=True) or {}

    nom = (data.get("nom") or "").strip()
    email = (data.get("email") or "").strip()
    sujet = (data.get("sujet") or "").strip()
    message = (data.get("message") or "").strip()

    if not all([nom, email, sujet, message]):
        return jsonify({"error": "Tous les champs sont obligatoires."}), 400

    contact = ContactMessage(nom=nom, email=email, sujet=sujet, message=message)
    db.session.add(contact)
    db.session.commit()

    envoyer_whatsapp(nom, email, sujet, message)

    return jsonify({"message": "Message envoyé avec succès."}), 201
