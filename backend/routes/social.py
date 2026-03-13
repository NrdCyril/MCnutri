from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Amitie, RecettePartagee, Message, Recette
from ..extensions import db
from datetime import datetime

social_bp = Blueprint("social", __name__)

# ── RECHERCHE UTILISATEUR ──────────────────────────────────────────
@social_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    user_id = int(get_jwt_identity())
    query   = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    users = User.query.filter(
    User.username.ilike(f'%{query}%'),
    User.user_id != user_id
    ).limit(10).all()

    return jsonify([{"id": u.user_id, "name": u.name, "username": u.username} for u in users])

# ── DEMANDE D'AMI ──────────────────────────────────────────────────
@social_bp.route('/amis/demande', methods=['POST'])
@jwt_required()
def envoyer_demande():
    user_id    = int(get_jwt_identity())
    receveur_id = request.json.get('receveur_id')

    if receveur_id == user_id:
        return jsonify({"error": "Vous ne pouvez pas vous ajouter vous-même"}), 400

    existant = Amitie.query.filter(
        ((Amitie.demandeur_id == user_id) & (Amitie.receveur_id == receveur_id)) |
        ((Amitie.demandeur_id == receveur_id) & (Amitie.receveur_id == user_id))
    ).first()

    if existant:
        return jsonify({"error": "Demande déjà existante ou déjà amis"}), 400

    amitie = Amitie(demandeur_id=user_id, receveur_id=receveur_id)
    db.session.add(amitie)
    db.session.commit()
    return jsonify({"message": "Demande envoyée"}), 201

# ── RÉPONDRE À UNE DEMANDE ─────────────────────────────────────────
@social_bp.route('/amis/demande/<int:amitie_id>', methods=['PATCH'])
@jwt_required()
def repondre_demande(amitie_id):
    user_id = int(get_jwt_identity())
    amitie  = Amitie.query.get_or_404(amitie_id)

    if amitie.receveur_id != user_id:
        return jsonify({"error": "Non autorisé"}), 403

    statut = request.json.get('statut')
    if statut not in ['accepte', 'refuse']:
        return jsonify({"error": "Statut invalide"}), 400

    amitie.statut = statut
    db.session.commit()
    return jsonify({"message": f"Demande {statut}"})

# ── LISTE DES AMIS ─────────────────────────────────────────────────
@social_bp.route('/amis', methods=['GET'])
@jwt_required()
def get_amis():
    user_id = int(get_jwt_identity())
    amities = Amitie.query.filter(
        ((Amitie.demandeur_id == user_id) | (Amitie.receveur_id == user_id)),
        Amitie.statut == 'accepte'
    ).all()

    amis = []
    for a in amities:
        ami_id  = a.receveur_id if a.demandeur_id == user_id else a.demandeur_id
        ami     = User.query.get(ami_id)
        non_lus = Message.query.filter_by(envoyeur_id=ami_id, receveur_id=user_id, lu=False).count()
        amis.append({
            "id":               ami.user_id,
            "name":             ami.name,
            "amitie_id":        a.id,
            "messages_non_lus": non_lus
        })
    return jsonify(amis)

# ── DEMANDES REÇUES EN ATTENTE ─────────────────────────────────────
@social_bp.route('/amis/demandes', methods=['GET'])
@jwt_required()
def get_demandes():
    user_id  = int(get_jwt_identity())
    demandes = Amitie.query.filter_by(receveur_id=user_id, statut='en_attente').all()
    result   = []
    for d in demandes:
        demandeur = User.query.get(d.demandeur_id)
        result.append({"amitie_id": d.id, "demandeur_id": d.demandeur_id, "name": demandeur.name})
    return jsonify(result)

# ── SUPPRIMER UN AMI ───────────────────────────────────────────────
@social_bp.route('/amis/<int:amitie_id>', methods=['DELETE'])
@jwt_required()
def supprimer_ami(amitie_id):
    user_id = int(get_jwt_identity())
    amitie  = Amitie.query.get_or_404(amitie_id)
    if amitie.demandeur_id != user_id and amitie.receveur_id != user_id:
        return jsonify({"error": "Non autorisé"}), 403
    db.session.delete(amitie)
    db.session.commit()
    return jsonify({"message": "Ami supprimé"})

# ── PARTAGER UNE RECETTE ───────────────────────────────────────────
@social_bp.route('/recettes/partager', methods=['POST'])
@jwt_required()
def partager_recette():
    user_id     = int(get_jwt_identity())
    data        = request.json
    recette_id  = data.get('recette_id')
    receveur_id = data.get('receveur_id')

    recette = Recette.query.filter_by(recette_id=recette_id, user_id=user_id).first()
    if not recette:
        return jsonify({"error": "Recette introuvable"}), 404

    partage = RecettePartagee(
        recette_id=recette_id,
        envoyeur_id=user_id,
        receveur_id=receveur_id
    )
    db.session.add(partage)

    envoyeur = User.query.get(user_id)
    nouvelle_recette = Recette(
        title=f"{recette.title} (partagée par {envoyeur.name})",
        instructions=recette.instructions,
        user_id=receveur_id
    )
    db.session.add(nouvelle_recette)
    db.session.flush()

    from ..models import Recette_Aliment
    for ra in recette.recette_aliments:
        nouveau_ra = Recette_Aliment(
            recette_id=nouvelle_recette.recette_id,
            aliment_id=ra.aliment_id,
            quantite=ra.quantite
        )
        db.session.add(nouveau_ra)

    db.session.commit()
    return jsonify({"message": "Recette partagée et ajoutée"}), 201

# ── RECETTES REÇUES ────────────────────────────────────────────────
@social_bp.route('/recettes/recues', methods=['GET'])
@jwt_required()
def recettes_recues():
    user_id  = int(get_jwt_identity())
    recettes = RecettePartagee.query.filter_by(receveur_id=user_id).order_by(RecettePartagee.date_envoi.desc()).all()
    result   = []
    for p in recettes:
        recette   = Recette.query.get(p.recette_id)
        envoyeur  = User.query.get(p.envoyeur_id)
        result.append({
            "id":           p.id,
            "recette_id":   p.recette_id,
            "title":        recette.title if recette else "Supprimée",
            "envoyeur":     envoyeur.name if envoyeur else "Inconnu",
            "date":         p.date_envoi.isoformat(),
            "lu":           p.lu
        })
    return jsonify(result)

# ── MESSAGES ───────────────────────────────────────────────────────
@social_bp.route('/messages/<int:ami_id>', methods=['GET'])
@jwt_required()
def get_messages(ami_id):
    user_id  = int(get_jwt_identity())
    messages = Message.query.filter(
        ((Message.envoyeur_id == user_id) & (Message.receveur_id == ami_id)) |
        ((Message.envoyeur_id == ami_id)  & (Message.receveur_id == user_id))
    ).order_by(Message.date_envoi).all()

    Message.query.filter_by(receveur_id=user_id, envoyeur_id=ami_id, lu=False).update({"lu": True})
    db.session.commit()

    return jsonify([{
        "id":          m.id,
        "envoyeur_id": m.envoyeur_id,
        "contenu":     m.contenu,
        "date":        m.date_envoi.isoformat(),
        "lu":          m.lu
    } for m in messages])

@social_bp.route('/messages', methods=['POST'])
@jwt_required()
def envoyer_message():
    user_id     = int(get_jwt_identity())
    data        = request.json
    receveur_id = data.get('receveur_id')
    contenu     = data.get('contenu', '').strip()

    if not contenu:
        return jsonify({"error": "Message vide"}), 400

    msg = Message(envoyeur_id=user_id, receveur_id=receveur_id, contenu=contenu)
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Message envoyé"}), 201

# ── NOTIFICATIONS (non lus) ────────────────────────────────────────
@social_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id           = int(get_jwt_identity())
    demandes          = Amitie.query.filter_by(receveur_id=user_id, statut='en_attente').count()
    messages_non_lus  = Message.query.filter_by(receveur_id=user_id, lu=False).count()
    recettes_non_lues = RecettePartagee.query.filter_by(receveur_id=user_id, lu=False).count()
    return jsonify({
        "demandes":        demandes,
        "messages":        messages_non_lus,
        "recettes_recues": recettes_non_lues,
        "total":           demandes + messages_non_lus + recettes_non_lues
    })

# ── MARQUER RECETTES REÇUES COMME LUES ────────────────────────────
@social_bp.route('/recettes/recues/lues', methods=['PATCH'])
@jwt_required()
def marquer_recettes_lues():
    user_id = int(get_jwt_identity())
    RecettePartagee.query.filter_by(receveur_id=user_id, lu=False).update({"lu": True})
    db.session.commit()
    return jsonify({"message": "Recettes marquées comme lues"})