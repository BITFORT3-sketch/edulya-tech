from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Purchase, Formation

achats_bp = Blueprint("achats", __name__, url_prefix="/api")


def _require_login():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


@achats_bp.route("/achats", methods=["POST"])
def acheter_formation():
    user_id = _require_login()
    if not user_id:
        return jsonify({"error": "Tu dois être connecté pour acheter une formation."}), 401

    data = request.get_json(silent=True) or {}
    formation_id = data.get("formation_id")

    formation = Formation.query.get(formation_id)
    if not formation:
        return jsonify({"error": "Formation introuvable."}), 404

    deja_achete = Purchase.query.filter_by(user_id=user_id, formation_id=formation_id).first()
    if deja_achete:
        return jsonify({"message": "Formation déjà achetée.", "achat": deja_achete.to_dict()}), 200

    achat = Purchase(user_id=user_id, formation_id=formation_id)
    db.session.add(achat)
    db.session.commit()

    return jsonify({"achat": achat.to_dict()}), 201

@achats_bp.route("/mes-achats", methods=["GET"])
def mes_achats():
    user_id = _require_login()
    if not user_id:
        return jsonify({"error": "Tu dois être connecté."}), 401

    achats = Purchase.query.filter_by(user_id=user_id).all()
    return jsonify({"achats": [a.to_dict() for a in achats]}), 200
