from flask import Blueprint, request, jsonify
from ..models import Aliment
from ..extensions import db
from ..decorators import role_required

aliments_bp = Blueprint("aliments", __name__)

@aliments_bp.route('/aliments', methods=['GET'])
def get_aliments():
    aliments = Aliment.query.all()
    return jsonify([{
        'id': a.id, 'name': a.name, 'calories': a.calories,
        'proteines': a.proteines, 'glucides': a.glucides, 'lipides': a.lipides
    } for a in aliments])

@aliments_bp.route('/aliments', methods=['POST'])
@role_required("admin", "dev")
def add_aliment():
    data = request.json
    a = Aliment(
        name=data['name'],
        calories=data.get('calories', 0.0),
        proteines=data.get('proteines', 0.0),
        glucides=data.get('glucides', 0.0),
        lipides=data.get('lipides', 0.0)
    )
    db.session.add(a)
    db.session.commit()
    return jsonify({'message': 'Aliment ajouté'}), 201

@aliments_bp.route('/aliments/<int:aliment_id>', methods=['PATCH'])
@role_required("admin", "dev")
def update_aliment(aliment_id):
    aliment = Aliment.query.get_or_404(aliment_id)
    data = request.json
    if "name"      in data: aliment.name      = data["name"]
    if "calories"  in data: aliment.calories  = data["calories"]
    if "proteines" in data: aliment.proteines = data["proteines"]
    if "glucides"  in data: aliment.glucides  = data["glucides"]
    if "lipides"   in data: aliment.lipides   = data["lipides"]
    db.session.commit()
    return jsonify({"message": "Aliment mis à jour"})

@aliments_bp.route('/aliments/<int:aliment_id>', methods=['DELETE'])
@role_required("admin", "dev")
def delete_aliment(aliment_id):
    aliment = Aliment.query.get_or_404(aliment_id)
    db.session.delete(aliment)
    db.session.commit()
    return jsonify({"message": "Aliment supprimé"})