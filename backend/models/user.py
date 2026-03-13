from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)

    age = db.Column(db.Integer)
    taille = db.Column(db.Float)
    poids = db.Column(db.Float)

    pw_hash = db.Column(db.String(200))

    role = db.Column(db.String(20), default="normal")

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)