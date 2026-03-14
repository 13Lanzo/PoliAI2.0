# PoliAI 2.0

PoliAI 2.0 è un assistente virtuale e chatbot per il Politecnico di Bari, sviluppato come progetto di tesi. Offre un'interfaccia conversazionale basata su intelligenza artificiale (Google Gemini) e fornisce supporto agli studenti fornendo informazioni sul campus, la generazione di immagini AI open-source (es. Stable Diffusion) e indicazioni su aule e strutture.

## Struttura del progetto
Il progetto è diviso in due parti principali:
* **Frontend**: Sviluppato in Angular (versione 17.3+)
* **Backend**: Sviluppato in Python con Flask e MySQL per la gestione degli utenti e messaggi.

## Prerequisiti
* Node.js e npm
* Python 3.x
* Server MySQL

## Configurazione Iniziale

### 1. Backend Setup
1. Spostati nella cartella `Backend`
2. Copia il file di esempio delle variabili d'ambiente:
   ```bash
   cp .env.example .env
   ```
3. Compila il file `.env` con le tue credenziali reali, inclusa la chiave API di Google Gemini (`GOOGLE_API_KEY`) e la connessione al database MySQL.
4. Crea e attiva un ambiente virtuale (es. `python -m venv venv`)
5. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
6. Avvia il server Flask:
   ```bash
   python run.py
   ```

### 2. Frontend Setup
1. Spostati nella cartella `Frontend`
2. Installa i pacchetti npm necessari:
   ```bash
   npm install
   ```
3. Avvia il server di sviluppo Angular:
   ```bash
   ng serve
   ```
4. L'interfaccia utente sarà disponibile all'indirizzo `http://localhost:4200/`.

## Sicurezza e Variabili d'Ambiente
> [!IMPORTANT]
> Non includere mai il file `.env` o file contenenti chiavi API hardcoded nei commit di Git. È stato configurato un `.gitignore` per ignorare tali file ed evitare l'esposizione accidentale di informazioni sensibili. Se stai clonando questa repository, dovrai configurare manualmente le API Keys e le credenziali di database indicate in `Backend/.env.example`.
