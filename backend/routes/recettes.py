from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Recette, Recette_Aliment, Aliment, User
from ..extensions import db
from ..ai_service import generate_recipe
import json, re
from datetime import date

recettes_bp = Blueprint("recettes", __name__)

@recettes_bp.route('/recettes', methods=['GET'])
@jwt_required()
def get_recettes():
    user_id = int(get_jwt_identity())
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)

    pagination = Recette.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for r in pagination.items:
        calories = proteines = glucides = lipides = 0
        for ra in r.recette_aliments:
            factor = float(ra.quantite) / 100
            a = ra.aliment
            calories  += a.calories  * factor
            proteines += a.proteines * factor
            glucides  += a.glucides  * factor
            lipides   += a.lipides   * factor
        result.append({
            'recette_id': r.recette_id,
            'title': r.title,
            'instructions': r.instructions,
            'nutrition': {
                'calories':  round(calories,  2),
                'proteines': round(proteines, 2),
                'glucides':  round(glucides,  2),
                'lipides':   round(lipides,   2)
            }
        })

    return jsonify({
        'recettes': result,
        'total':    pagination.total,
        'pages':    pagination.pages,
        'page':     pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@recettes_bp.route('/recettes/<int:recette_id>', methods=['DELETE'])
@jwt_required()
def delete_recette(recette_id):
    user_id = int(get_jwt_identity())
    recette = Recette.query.filter_by(recette_id=recette_id, user_id=user_id).first()
    
    if not recette:
        return jsonify({"error": "Recette introuvable ou non autorisée"}), 404

    Recette_Aliment.query.filter_by(recette_id=recette_id).delete()
    db.session.delete(recette)
    db.session.commit()
    return jsonify({"message": "Recette supprimée"}), 200

@recettes_bp.route('/generate_recette', methods=['POST'])
@jwt_required()
def generate_recette():
    data = request.json
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    regime = user.regime or "standard"

    prompt = f"""
    Génère une recette fitness adaptée au régime {regime}.
    Contraintes ingrédients : {data.get('ingredients', '')}
    Répond STRICTEMENT en JSON.
    """
    recette_text = generate_recipe(prompt)

    match = re.search(r"\{.*\}", recette_text, re.DOTALL)
    if not match:
        return jsonify({"error": "Impossible de parser l'IA"}), 500
    recette_ia = json.loads(match.group(0))

    instructions = recette_ia["instructions"]
    if isinstance(instructions, list):
        instructions = "\n".join(instructions)

    recette = Recette(title=recette_ia["title"], instructions=instructions, user_id=user_id)
    db.session.add(recette)
    db.session.commit()

    for ingredient in recette_ia["ingredients"]:
        aliment_db = Aliment.query.filter(Aliment.name.ilike(ingredient["name"])).first()
        if aliment_db:
            ra = Recette_Aliment(recette_id=recette.recette_id, aliment_id=aliment_db.id,
                                 quantite=float(ingredient.get("quantite", 100)))
            db.session.add(ra)
    db.session.commit()

    calories = proteines = glucides = lipides = 0
    for ra in recette.recette_aliments:
        factor = float(ra.quantite) / 100
        a = ra.aliment
        calories  += a.calories  * factor
        proteines += a.proteines * factor
        glucides  += a.glucides  * factor
        lipides   += a.lipides   * factor

    return jsonify({
        "title": recette.title,
        "instructions": recette.instructions,
        "nutrition": {
            "calories":  round(calories,  2),
            "proteines": round(proteines, 2),
            "glucides":  round(glucides,  2),
            "lipides":   round(lipides,   2)
        }
    })

@recettes_bp.route('/recettes/<int:recette_id>/ajouter-stats', methods=['POST'])
@jwt_required()
def ajouter_recette_stats(recette_id):
    user_id = int(get_jwt_identity())
    recette = Recette.query.filter_by(recette_id=recette_id, user_id=user_id).first_or_404()

    calories = proteines = glucides = lipides = 0
    for ra in recette.recette_aliments:
        factor = float(ra.quantite) / 100
        a = ra.aliment
        calories  += a.calories  * factor
        proteines += a.proteines * factor
        glucides  += a.glucides  * factor
        lipides   += a.lipides   * factor

    from .stats import stats_bp
    from ..models import Repas
    repas = Repas(
        user_id=user_id,
        nom=recette.title,
        date=date.today(),
        calories=round(calories, 1),
        proteines=round(proteines, 1),
        glucides=round(glucides, 1),
        lipides=round(lipides, 1)
    )
    db.session.add(repas)
    db.session.commit()
    return jsonify({"message": "Recette ajoutée aux stats"}), 201