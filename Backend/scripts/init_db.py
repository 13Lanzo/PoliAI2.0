import os
import sys

# Aggiungi il percorso di base al sistema per importazioni
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)

from app import create_app
from app.utils.db import db
from app.models.db_models import Dipartimento, Corso, AziendaPartner

# Creare l'app in modo fittizio per il contesto DB
app = create_app()

def init_db():
    with app.app_context():
        # Crea tutte le tabelle partendo dai modelli definiti
        db.create_all()
        print("[OK] Tabelle nel Database MySQL Create Correttamente!")

        # Popoliamo qualche dato di esempio
        if Dipartimento.query.count() == 0:
            print("[*] Inserimento Dati di Esempio nei Dipartimenti...")
            dei = Dipartimento(nome="DEI - Dipartimento di Ingegneria Elettrica e dell'Informazione", descrizione="Dipartimento incentrato su elettronica, informatica e telecomunicazioni.")
            dmmm = Dipartimento(nome="DMMM - Dipartimento di Meccanica, Matematica e Management", descrizione="Ingegneria meccanica gestionale e affini")
            dicar = Dipartimento(nome="DICAR - Dipartimento di Ingegneria Civile, Ambientale, del Territorio", descrizione="Architettura e civile")
            db.session.add_all([dei, dmmm, dicar])
            db.session.commit()
            
            # Corsi Esempio
            corso_inf = Corso(nome="Ingegneria Informatica e dell'Automazione", tipo_laurea="Triennale", classe_laurea="L-8", dipartimento=dei, sbocchi_lavorativi="Sviluppatore Software, Ingegnere del Cloud, Data Analyst")
            corso_mec = Corso(nome="Ingegneria Meccanica", tipo_laurea="Triennale", classe_laurea="L-9", dipartimento=dmmm, sbocchi_lavorativi="Progettista meccanico, Impiantista")
            db.session.add_all([corso_inf, corso_mec])

            # Partner
            azienda = AziendaPartner(nome="Fincons Group", settore="IT Consulting", descrizione="Partner storico del DEI Poliba per tirocini e assunzioni")
            db.session.add_all([azienda])

            db.session.commit()
            print("[OK] Dati di Base Inseriti.")

if __name__ == "__main__":
    init_db()
