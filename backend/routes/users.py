from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from ..extensions import db
from ..models import User, Mesure
from datetime import date as DateType

users_bp = Blueprint("users", __name__)


@users_bp.route("/me")
@jwt_required()
def me():

    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)

    return jsonify({
        "id": user.user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "taille": user.taille,
        "poids": user.poids,
        "role": user.role,
        "regime": user.regime,
        "langue": user.langue or 'fr'
    })

@users_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.json

    if "name" in data:
        user.name = data["name"]
    if "age" in data:
        user.age = data["age"]
    if "taille" in data:
        user.taille = data["taille"]
    if "poids" in data:
        user.poids = data["poids"]
    if 'langue' in data:
        user.langue = data['langue']
    if "regime" in data:
        if data["regime"] not in ["standard", "vegetarien", "vegan"]:
            return jsonify({"error": "Régime invalide"}), 400
        user.regime = data["regime"]

    db.session.commit()
    return jsonify({"message": "Profil mis à jour"})

@users_bp.route("/mesures", methods=['GET'])
@jwt_required()
def get_mesures():
    user_id = int(get_jwt_identity())
    mesures = Mesure.query.filter_by(user_id=user_id).order_by(Mesure.date).all()
    return jsonify([{
        "id": m.id,
        "date": m.date.isoformat(),
        "poids": m.poids,
        "masse_grasse": m.masse_grasse
    } for m in mesures])

@users_bp.route("/mesures", methods=['POST'])
@jwt_required()
def add_mesure():
    user_id = int(get_jwt_identity())
    data = request.json
    mesure = Mesure(
        user_id=user_id,
        date=DateType.fromisoformat(data['date']),
        poids=data['poids'],
        masse_grasse=data.get('masse_grasse', None)
    )
    db.session.add(mesure)
    db.session.commit()
    return jsonify({"message": "Mesure enregistrée"}), 201