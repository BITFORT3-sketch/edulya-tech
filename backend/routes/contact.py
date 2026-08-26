from flask import Blueprint, request, jsonify
from extensions import db
from models import ContactMessage

contact_bp = Blueprint("contact", __name__, url_prefix="/api")


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

    return jsonify({"message": "Message envoyé avec succès."}), 201
