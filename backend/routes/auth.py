from flask import Blueprint, request, jsonify
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from ..models import User
from ..extensions import db, mail
from flask_jwt_extended import create_access_token
import os

auth_bp = Blueprint('auth', __name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email et mot de passe obligatoires'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.user_id),
                                           additional_claims={"role": user.role})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    if not data.get('name'):
        return jsonify({'message': 'Le nom est obligatoire'}), 400
    if not data.get('email'):
        return jsonify({'message': 'L\'email est obligatoire'}), 400
    if not data.get('password'):
        return jsonify({'message': 'Le mot de passe est obligatoire'}), 400
    if len(data['password']) < 8:
        return jsonify({'message': 'Le mot de passe doit contenir au moins 8 caractères'}), 400

    if not data.get('username'):
        return jsonify({'message': 'Le pseudo est obligatoire'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Ce pseudo est déjà pris'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email déjà utilisé'}), 400

    user = User(
        name=data['name'],
        username=data['username'],
        age=data.get('age'),
        taille=data.get('taille'),
        poids=data.get('poids'),
        email=data['email'],
        regime=data.get('regime', 'standard')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur créé'}), 201


def get_serializer():
    return URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "supersecret"))

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()

    # On répond toujours OK pour ne pas révéler si l'email existe
    if not user:
        return jsonify({"message": "Si cet email existe, un lien a été envoyé"}), 200

    token = get_serializer().dumps(user.email, salt="reset-password")
    reset_url = f"http://localhost:8080/reset-password.html?token={token}"

    msg = Message(
        subject="Réinitialisation de votre mot de passe MCNutri",
        recipients=[user.email],
        body=f"""Bonjour {user.name},

Vous avez demandé la réinitialisation de votre mot de passe.
Cliquez sur ce lien (valable 30 minutes) :

{reset_url}

Si vous n'avez pas fait cette demande, ignorez cet email.
"""
    )
    mail.send(msg)
    return jsonify({"message": "Si cet email existe, un lien a été envoyé"}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('password')

    try:
        email = get_serializer().loads(token, salt="reset-password", max_age=1800)
    except SignatureExpired:
        return jsonify({"error": "Lien expiré"}), 400
    except BadSignature:
        return jsonify({"error": "Lien invalide"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Mot de passe réinitialisé avec succès"}), 200