from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Recette, Recette_Aliment, Aliment, Repas
from ..extensions import db
from datetime import date, timedelta, datetime
import math

stats_bp = Blueprint("stats", __name__)

def get_period_bounds(periode):
    today = date.today()
    if periode == 'today':
        start = today
        end   = today
    elif periode == 'semaine':
        start = today - timedelta(days=today.weekday())
        end   = today
    else:  # mois
        start = today.replace(day=1)
        end   = today
    return start, end

# ── STATS NUTRITIONNELLES ──────────────────────────────────────────
@stats_bp.route('/stats/nutrition', methods=['GET'])
@jwt_required()
def stats_nutrition():
    user_id = int(get_jwt_identity())
    periode = request.args.get('periode', 'semaine')  # 'semaine' ou 'mois'
    start, end = get_period_bounds(periode)

    # Macros depuis les recettes sauvegardées dans la période
    recettes = Recette.query.filter(
        Recette.user_id == user_id,
        Recette.created_at >= datetime.combine(start, datetime.min.time()),
        Recette.created_at <= datetime.combine(end, datetime.max.time())
    ).all()

    stats_recettes = {"calories": 0, "proteines": 0, "glucides": 0, "lipides": 0, "count": len(recettes)}
    for r in recettes:
        for ra in r.recette_aliments:
            factor = float(ra.quantite) / 100
            a = ra.aliment
            stats_recettes["calories"]  += a.calories  * factor
            stats_recettes["proteines"] += a.proteines * factor
            stats_recettes["glucides"]  += a.glucides  * factor
            stats_recettes["lipides"]   += a.lipides   * factor

    # Macros depuis les repas manuels dans la période
    repas_liste = Repas.query.filter(
        Repas.user_id == user_id,
        Repas.date >= start,
        Repas.date <= end
    ).all()

    stats_repas = {"calories": 0, "proteines": 0, "glucides": 0, "lipides": 0, "count": len(repas_liste)}
    for rep in repas_liste:
        stats_repas["calories"]  += rep.calories  or 0
        stats_repas["proteines"] += rep.proteines or 0
        stats_repas["glucides"]  += rep.glucides  or 0
        stats_repas["lipides"]   += rep.lipides   or 0

    # Données jour par jour pour le graphique
    nb_days = (end - start).days + 1
    jours = []
    for i in range(nb_days):
        jour = start + timedelta(days=i)
        cal_recettes = 0
        for r in recettes:
            if r.created_at and r.created_at.date() == jour:
                for ra in r.recette_aliments:
                    cal_recettes += ra.aliment.calories * float(ra.quantite) / 100
        cal_repas = sum(rep.calories or 0 for rep in repas_liste if rep.date == jour)
        jours.append({
            "date":     jour.isoformat(),
            "label": jour.strftime("%H:%M") if periode == "today" else jour.strftime("%a %d" if periode == "semaine" else "%d/%m"),
            "calories": round(cal_recettes + cal_repas, 1)
        })

    # Totaux combinés
    totaux = {
        "calories":  round(stats_recettes["calories"]  + stats_repas["calories"],  1),
        "proteines": round(stats_recettes["proteines"] + stats_repas["proteines"], 1),
        "glucides":  round(stats_recettes["glucides"]  + stats_repas["glucides"],  1),
        "lipides":   round(stats_recettes["lipides"]   + stats_repas["lipides"],   1),
    }

    nb_jours_actifs = nb_days
    moyennes = {k: round(v / nb_jours_actifs, 1) for k, v in totaux.items()}

    return jsonify({
        "periode":   periode,
        "start":     start.isoformat(),
        "end":       end.isoformat(),
        "totaux":    totaux,
        "moyennes":  moyennes,
        "recettes":  {k: round(v, 1) for k, v in stats_recettes.items()},
        "repas":     {k: round(v, 1) if isinstance(v, float) else v for k, v in stats_repas.items()},
        "jours":     jours
    })

# ── REPAS MANUELS ──────────────────────────────────────────────────
@stats_bp.route('/repas', methods=['GET'])
@jwt_required()
def get_repas():
    user_id = int(get_jwt_identity())
    periode = request.args.get('periode', 'semaine')
    start, end = get_period_bounds(periode)
    repas = Repas.query.filter(
        Repas.user_id == user_id,
        Repas.date >= start,
        Repas.date <= end
    ).order_by(Repas.date.desc()).all()
    return jsonify([{
        "id":        r.id,
        "nom":       r.nom,
        "date":      r.date.isoformat(),
        "calories":  r.calories,
        "proteines": r.proteines,
        "glucides":  r.glucides,
        "lipides":   r.lipides
    } for r in repas])

@stats_bp.route('/repas', methods=['POST'])
@jwt_required()
def add_repas():
    user_id = int(get_jwt_identity())
    data = request.json
    if not data.get('nom'):
        return jsonify({"error": "Le nom est obligatoire"}), 400
    repas = Repas(
        user_id=user_id,
        nom=data['nom'],
        date=date.fromisoformat(data.get('date', date.today().isoformat())),
        calories=float(data.get('calories', 0)),
        proteines=float(data.get('proteines', 0)),
        glucides=float(data.get('glucides', 0)),
        lipides=float(data.get('lipides', 0))
    )
    db.session.add(repas)
    db.session.commit()
    return jsonify({"message": "Repas enregistré"}), 201

@stats_bp.route('/repas/<int:repas_id>', methods=['DELETE'])
@jwt_required()
def delete_repas(repas_id):
    user_id = int(get_jwt_identity())
    repas = Repas.query.filter_by(id=repas_id, user_id=user_id).first_or_404()
    db.session.delete(repas)
    db.session.commit()
    return jsonify({"message": "Repas supprimé"})

# ── SANTÉ : IMC + CALORIES JOURNALIÈRES ───────────────────────────
@stats_bp.route('/sante', methods=['GET'])
@jwt_required()
def sante():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    result = {"imc": None, "imc_categorie": None, "calories_maintenance": None,
              "calories_perte": None, "calories_prise": None,
              "poids": user.poids, "taille": user.taille, "age": user.age}

    if not user.poids or not user.taille:
        return jsonify(result)

    taille_m = user.taille / 100
    imc = round(user.poids / (taille_m ** 2), 1)

    if imc < 18.5:    cat = "Insuffisance pondérale"
    elif imc < 25:    cat = "Poids normal"
    elif imc < 30:    cat = "Surpoids"
    elif imc < 35:    cat = "Obésité modérée"
    else:             cat = "Obésité sévère"

    # Formule de Mifflin-St Jeor (on suppose homme par défaut, à affiner si genre ajouté)
    if user.age:
        bmr = 10 * user.poids + 6.25 * user.taille - 5 * user.age + 5
    else:
        bmr = 10 * user.poids + 6.25 * user.taille - 5 * 25 + 5  # âge par défaut 25

    maintenance = round(bmr * 1.55)  # activité modérée

    # Protéines recommandées (1.6g à 2.2g par kg de poids corporel pour sportif)
    proteines_min = round(user.poids * 1.6, 0)
    proteines_max = round(user.poids * 2.2, 0)

    result.update({
        "imc":                  imc,
        "imc_categorie":        cat,
        "bmr":                  round(bmr),
        "calories_maintenance": maintenance,
        "calories_perte":       round(maintenance * 0.8),
        "calories_prise":       round(maintenance * 1.15),
        "proteines_min":        int(proteines_min),
        "proteines_max":        int(proteines_max),
    })
    return jsonify(result)
