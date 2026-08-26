from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Avis, Purchase, Formation

avis_bp = Blueprint("avis", __name__, url_prefix="/api")


def _acces_autorise(user_id, formation_id):
    """Un avis ne peut être lu ou écrit que par quelqu'un qui a acheté
    la formation — vérifié côté serveur, comme pour le téléchargement."""
    if not user_id:
        return False
    return Purchase.query.filter_by(user_id=user_id, formation_id=formation_id).first() is not None


@avis_bp.route("/formations/<formation_id>/avis", methods=["GET"])
def lister_avis(formation_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Connexion requise."}), 401

    if not Formation.query.get(formation_id):
        return jsonify({"error": "Formation introuvable."}), 404

    if not _acces_autorise(user_id, formation_id):
        return jsonify({"error": "Tu dois avoir acheté cette formation pour voir les avis."}), 403

    avis = (
        Avis.query.filter_by(formation_id=formation_id)
        .order_by(Avis.date_envoi.asc())
        .all()
    )
    return jsonify({"avis": [a.to_dict() for a in avis]}), 200


@avis_bp.route("/formations/<formation_id>/avis", methods=["POST"])
def poster_avis(formation_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Connexion requise."}), 401

    if not Formation.query.get(formation_id):
        return jsonify({"error": "Formation introuvable."}), 404

    if not _acces_autorise(user_id, formation_id):
        return jsonify({"error": "Tu dois avoir acheté cette formation pour laisser un avis."}), 403

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Le message ne peut pas être vide."}), 400
    if len(message) > 500:
        return jsonify({"error": "Le message est trop long (500 caractères max)."}), 400

    avis = Avis(user_id=user_id, formation_id=formation_id, message=message)
    db.session.add(avis)
    db.session.commit()

    return jsonify({"avis": avis.to_dict()}), 201
