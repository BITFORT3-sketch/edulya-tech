from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import os

from extensions import db
from models import User, Purchase, Avis
from mail_utils import envoyer_email_reinitialisation
from rate_limit import trop_de_tentatives, enregistrer_tentative, reinitialiser_tentatives

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    nom = (data.get("nom") or "").strip()
    prenom = (data.get("prenom") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telephone = (data.get("telephone") or "").strip()
    password = data.get("password") or ""

    if not all([nom, prenom, email, telephone, password]):
        return jsonify({"error": "Tous les champs sont obligatoires."}), 400

    if len(password) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Un compte existe déjà avec cet email."}), 409

    user = User(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    session.permanent = True
    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    cle_limite = f"login:{email}"
    if trop_de_tentatives(cle_limite, max_tentatives=5, fenetre_secondes=15 * 60):
        return jsonify({
            "error": "Trop de tentatives de connexion. Réessaie dans quelques minutes."
        }), 429

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        enregistrer_tentative(cle_limite)
        return jsonify({"error": "Email ou mot de passe incorrect."}), 401

    reinitialiser_tentatives(cle_limite)
    session.permanent = True
    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Déconnecté."}), 200


@auth_bp.route("/compte", methods=["DELETE"])
def supprimer_compte():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Connexion requise."}), 401

    user = User.query.get(user_id)
    if not user:
        session.pop("user_id", None)
        return jsonify({"error": "Compte introuvable."}), 404

    # On supprime d'abord ce qui dépend du compte (achats, avis), puis le
    # compte lui-même, pour respecter les clés étrangères.
    Avis.query.filter_by(user_id=user_id).delete()
    Purchase.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    session.pop("user_id", None)
    return jsonify({"message": "Compte supprimé."}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None}), 200

    user = User.query.get(user_id)
    if not user:
        session.pop("user_id", None)
        return jsonify({"user": None}), 200

    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/mot-de-passe-oublie", methods=["POST"])
def mot_de_passe_oublie():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    # Réponse générique dans tous les cas (compte trouvé ou non), pour ne pas
    # révéler quels emails sont enregistrés dans la base.
    reponse_generique = jsonify({
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    })

    if not email:
        return reponse_generique, 200

    cle_limite = f"reset:{email}"
    if trop_de_tentatives(cle_limite, max_tentatives=3, fenetre_secondes=15 * 60):
        # Même réponse générique volontairement — on ne révèle pas qu'une
        # limite existe, pour ne pas donner d'indice à quelqu'un qui teste
        # des emails au hasard.
        return reponse_generique, 200
    enregistrer_tentative(cle_limite)

    user = User.query.filter_by(email=email).first()
    if not user:
        return reponse_generique, 200

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    frontend_url = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5500")
    lien = f"{frontend_url}/reinitialiser-mot-de-passe.html?token={token}"
    envoyer_email_reinitialisation(user.email, lien)

    return reponse_generique, 200


@auth_bp.route("/reinitialiser-mot-de-passe", methods=["POST"])
def reinitialiser_mot_de_passe():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    password = data.get("password") or ""

    if not token or not password:
        return jsonify({"error": "Lien invalide."}), 400

    if len(password) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return jsonify({"error": "Ce lien de réinitialisation est invalide ou a expiré."}), 400

    user.password_hash = generate_password_hash(password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Mot de passe modifié avec succès."}), 200
