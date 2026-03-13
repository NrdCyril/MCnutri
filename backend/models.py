from datetime import datetime
from .extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)
    langue = db.Column(db.String(5), default='fr')
    age = db.Column(db.Integer)
    taille = db.Column(db.Float)
    poids = db.Column(db.Float)
    email = db.Column(db.String(150), unique=True, nullable=False)
    pw_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="normal")  # normal | premium | admin
    regime = db.Column(db.String(20), default="standard")  # standard | vegetarien | vegan

    recettes = db.relationship('Recette', backref='author', lazy=True)

    def set_password(self, password):
        self.pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.pw_hash, password)

class Recette(db.Model):
    __tablename__ = 'recette'
    recette_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    recette_aliments = db.relationship('Recette_Aliment', backref='recette', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Aliment(db.Model):
    __tablename__ = 'aliment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, default=0.0)
    proteines = db.Column(db.Float, default=0.0)
    glucides = db.Column(db.Float, default=0.0)
    lipides = db.Column(db.Float, default=0.0)
    recettes = db.relationship('Recette_Aliment', backref='aliment', lazy=True)

class Recette_Aliment(db.Model):
    __tablename__ = 'recette_aliment'
    recette_id = db.Column(db.Integer, db.ForeignKey('recette.recette_id'), primary_key=True)
    aliment_id = db.Column(db.Integer, db.ForeignKey('aliment.id'), primary_key=True)
    quantite = db.Column(db.Float, default=100)

class Mesure(db.Model):
    __tablename__ = 'mesure'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    poids = db.Column(db.Float, nullable=False)
    masse_grasse = db.Column(db.Float, nullable=True)


class Amitie(db.Model):
    __tablename__ = 'amitie'
    id = db.Column(db.Integer, primary_key=True)
    demandeur_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receveur_id  = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    statut = db.Column(db.String(20), default="en_attente")  # en_attente | accepte | refuse

class RecettePartagee(db.Model):
    __tablename__ = 'recette_partagee'
    id = db.Column(db.Integer, primary_key=True)
    recette_id   = db.Column(db.Integer, db.ForeignKey('recette.recette_id'), nullable=False)
    envoyeur_id  = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receveur_id  = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date_envoi   = db.Column(db.DateTime, default=db.func.now())
    lu           = db.Column(db.Boolean, default=False)

class Message(db.Model):
    __tablename__ = 'message'
    id           = db.Column(db.Integer, primary_key=True)
    envoyeur_id  = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receveur_id  = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    contenu      = db.Column(db.Text, nullable=False)
    date_envoi   = db.Column(db.DateTime, default=db.func.now())
    lu           = db.Column(db.Boolean, default=False)

class Repas(db.Model):
    __tablename__ = 'repas'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    nom       = db.Column(db.String(200), nullable=False)
    date      = db.Column(db.Date, nullable=False)
    calories  = db.Column(db.Float, default=0)
    proteines = db.Column(db.Float, default=0)
    glucides  = db.Column(db.Float, default=0)
    lipides   = db.Column(db.Float, default=0)