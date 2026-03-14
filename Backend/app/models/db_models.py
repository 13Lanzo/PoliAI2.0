from app.utils.db import db

class Dipartimento(db.Model):
    __tablename__ = 'dipartimenti'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text, nullable=True)

    # Relazione 1 a N con i Corsi
    corsi = db.relationship('Corso', backref='dipartimento', lazy=True)

class Corso(db.Model):
    __tablename__ = 'corsi'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo_laurea = db.Column(db.String(50), nullable=False) # "Triennale", "Magistrale"
    classe_laurea = db.Column(db.String(10), nullable=False)
    dipartimento_id = db.Column(db.Integer, db.ForeignKey('dipartimenti.id'), nullable=False)
    descrizione = db.Column(db.Text, nullable=True)
    sbocchi_lavorativi = db.Column(db.Text, nullable=True)

class AziendaPartner(db.Model):
    __tablename__ = 'aziende_partner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    settore = db.Column(db.String(100), nullable=True)
    descrizione = db.Column(db.Text, nullable=True)
