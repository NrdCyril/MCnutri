from flask import Blueprint, jsonify, request
from ..models import User
from ..extensions import db
from ..decorators import role_required

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

from flask import Blueprint, jsonify, request
from ..models import User
from ..extensions import db
from ..decorators import role_required

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/users")
@role_required("admin", "dev")
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.user_id, "name": u.name, "role": u.role}
        for u in users
    ])

@admin_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@role_required("admin", "dev")
def update_role(user_id):
    data = request.json
    user = User.query.get_or_404(user_id)

    # Un compte dev ne peut jamais être modifié
    if user.role == "dev":
        return jsonify({"error": "Ce compte ne peut pas être modifié"}), 403

    # Le rôle dev ne peut pas être attribué via l'API
    if data.get("role") not in ["normal", "premium", "admin"]:
        return jsonify({"error": "Rôle invalide"}), 400

    user.role = data["role"]
    db.session.commit()
    return jsonify({"message": f"Rôle mis à jour : {user.role}"})

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@role_required("admin", "dev")
def delete_user(user_id):
    from flask_jwt_extended import get_jwt_identity, get_jwt
    from flask import request as freq

    claims = get_jwt()
    requester_role = claims.get("role")
    requester_id = int(get_jwt_identity())

    user = User.query.get_or_404(user_id)

    # Empêcher la suppression d'un compte dev (sauf par lui-même, non autorisé aussi)
    if user.role == "dev":
        return jsonify({"error": "Un compte dev ne peut pas être supprimé"}), 403

    # Empêcher un admin de supprimer un autre admin
    if requester_role == "admin" and user.role == "admin":
        return jsonify({"error": "Un admin ne peut pas supprimer un autre admin"}), 403

    # Empêcher l'auto-suppression
    if requester_id == user_id:
        return jsonify({"error": "Vous ne pouvez pas supprimer votre propre compte"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Compte {user.name} supprimé"}), 200