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


@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method=="OPTIONS":
        return "",200
        
    data = request.get_json(silent=True) or {}

    nom = (data.get("nom") or "").strip()
    prenom = (data.get("prenom") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telephone = (data.get("telephone") or "").strip()
    password = data.get("password") or ""
    conditions_acceptees = bool(data.get("conditions_acceptees", False))

    if not all([nom, prenom, email, telephone, password]):
        return jsonify({"error": "Tous les champs sont obligatoires."}), 400

    if len(password) < 8:
        return jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}), 400

    if not conditions_acceptees:
        return jsonify({"error": "Tu dois accepter les conditions générales et la politique de confidentialité."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Un compte existe déjà avec cet email."}), 409

    user = User(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        password_hash=generate_password_hash(password),
        conditions_acceptees=True,
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


@auth_bp.route("/supprimer-compte", methods=["DELETE", "POST"])
def supprimer_compte():
    """Supprime définitivement le compte connecté et ses données liées."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Tu dois être connecté pour supprimer ton compte."}), 401

    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""
    user = User.query.get(user_id)
    if not user:
        session.pop("user_id", None)
        return jsonify({"error": "Compte introuvable."}), 404

    if not password or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Mot de passe incorrect. Le compte n'a pas été supprimé."}), 403

    # Les données liées doivent être supprimées avant l'utilisateur pour éviter
    # une violation des clés étrangères sur PostgreSQL.
    Avis.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Purchase.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()
    session.clear()

    return jsonify({"message": "Ton compte et les données associées ont été supprimés définitivement."}), 200


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

    # En production, FRONTEND_URL est recommandé. L'Origin du navigateur
    # sert de secours lorsque le frontend est hébergé sur un autre domaine.
    frontend_url = (
        os.environ.get("FRONTEND_URL")
        or request.headers.get("Origin")
        or "http://127.0.0.1:5500"
    ).rstrip("/")
    lien = f"{frontend_url}/reinitialiser-mot-de-passe.html?token={token}"
    email_envoye = envoyer_email_reinitialisation(user.email, lien)
    if not email_envoye:
        print("[RESET] Le lien a été généré mais l'email n'a pas pu être envoyé. Vérifie MAIL_* sur Render.")

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
