from flask import Blueprint, jsonify, session, redirect
from models import Formation, Purchase

formations_bp = Blueprint("formations", __name__, url_prefix="/api")


@formations_bp.route("/formations", methods=["GET"])
def list_formations():
    formations = Formation.query.all()
    return jsonify({"formations": [f.to_dict() for f in formations]}), 200


@formations_bp.route("/formations/<formation_id>", methods=["GET"])
def get_formation(formation_id):
    formation = Formation.query.get(formation_id)
    if not formation:
        return jsonify({"error": "Formation introuvable."}), 404
    return jsonify({"formation": formation.to_dict()}), 200


@formations_bp.route("/formations/<formation_id>/telecharger", methods=["GET"])
def telecharger_formation(formation_id):
    """
    Route protégée : vérifie CÔTÉ SERVEUR (jamais seulement côté frontend)
    que l'utilisateur est connecté ET a bien acheté cette formation avant de
    le rediriger vers le PDF. Le lien réel (Drive) n'est jamais renvoyé dans
    une réponse JSON — il n'existe que dans cette redirection, après contrôle.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Connexion requise."}), 401

    possede = Purchase.query.filter_by(user_id=user_id, formation_id=formation_id).first()
    if not possede:
        return jsonify({"error": "Tu n'as pas accès à cette formation."}), 403

    formation = Formation.query.get(formation_id)
    if not formation or not formation.ressource_url:
        return jsonify({"error": "Aucune ressource disponible pour cette formation."}), 404

    return redirect(formation.ressource_url)
