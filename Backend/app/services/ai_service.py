import os
import chromadb
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.models.db_models import Corso, AziendaPartner, Dipartimento
from sentence_transformers import cross_encoder

class AIOrientationService:
    def __init__(self):
        # 1. Inizializzare l'LLM principale (Gemini Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0.3,
            max_tokens=1000,
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        )
        
        # 2. Inizializzare connessione ChromaDB persistente
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        chroma_path = os.path.join(base_dir, 'data', 'chroma_db')
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        try:
             self.collection = self.chroma_client.get_collection("polibai_docs")
        except Exception:
             self.collection = None

    def hybrid_orchestrator(self, user_query):
        """
        L'Orchestratore: decide se la query richiede dati strutturati (MySQL),
        o documenti non strutturati (ChromaDB), o una combinazione.
        """
        # Creiamo un prompt di classificazione invisibile per Gemini
        routing_prompt = f"""
        Sei il Router AI del Politecnico di Bari. Devi classificare la seguente domanda dello studente.
        Rispondi ESATTAMENTE con una di queste 3 categorie:
        1. "STRUTTURATO": se chiede informazioni su Corsi di laurea, dipartimenti (DEI, DMMM, DICAR), o aziende partner con cui collaboriamo.
        2. "DOCUMENTALE": se chiede informazioni amministrative, bandi Erasmus, regolamenti tasse, ISEE, o regole di ateneo.
        3. "IBRIDO": se chiede informazioni miste o necessita un ragionamento di orientamento complesso (es. "Mi piace la robotica, che corso scelgo e quanto pago di ISEE?").

        Domanda dell'utente: "{user_query}"
        Categoria:
        """
        
        routing_decision = self.llm.invoke(routing_prompt).content.strip().upper()
        
        context = ""
        
        # Branch 1: Dati Strutturati (MySQL)
        if "STRUTTURATO" in routing_decision or "IBRIDO" in routing_decision:
            context += self._fetch_mysql_context(user_query)
            
        # Branch 2: Dati Documentali (ChromaDB / RAG)
        if "DOCUMENTALE" in routing_decision or "IBRIDO" in routing_decision:
            context += self._fetch_chroma_context(user_query)
            
        # Generazione Finale
        final_response = self._generate_answer(user_query, context)
        return {
            "answer": final_response,
            "routing": routing_decision
        }

    def _fetch_mysql_context(self, query):
        """Estrae i corsi e dipartimenti dal database relazionale."""
        # Per una POC, carichiamo tutti i corsi.
        # In produzione si userebbe una Full-Text Search o Vector Search su MySQL se supportato
        corsi = Corso.query.all()
        context = "### DATI UFFICIALI (Database Poliba) ###\n"
        for c in corsi:
            context += f"- Corso: {c.nome} ({c.tipo_laurea}, {c.classe_laurea}). Dipartimento ID: {c.dipartimento_id}. Sbocchi: {c.sbocchi_lavorativi}\n"
        
        aziende = AziendaPartner.query.all()
        context += "Aziende Partner: " + ", ".join([a.nome for a in aziende]) + "\n\n"
        return context

    def _fetch_chroma_context(self, query):
        """Usa RAG puro per recuperare info amministrative."""
        if not self.collection:
            return "Nessun bando o regolamento attualmente caricato nel sistema.\n"
            
        # Calcoliamo l'embedding della query
        query_embedding = self.embeddings.embed_query(query)
        
        # Recupero dal DB Vettoriale
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        context = "### TESTI UFFICIALI (Bandi e Regolamenti) ###\n"
        if results and results['documents']:
            for idx, doc in enumerate(results['documents'][0]):
                source = results['metadatas'][0][idx].get('source', 'Sconosciuta')
                context += f"[Fonte: {source}]: {doc}\n\n"
                
        return context

    def _generate_answer(self, query, combined_context):
        """Prompt finale per l'Engine di generazione."""
        system_prompt = f"""
        Sei PolibAI 2.0, l'assistente ufficiale all'orientamento del Politecnico di Bari.
        Sei professionale, accogliente e aiuti i futuri studenti.
        Utilizza le informazioni di contesto fornite per rispondere.
        
        REGOLE DI BUSINESS OBBLIGATORIE:
        1. REGOLE FINANZIARIE E TASSE:
           - Se l'utente chiede il calcolo delle tasse o menziona un ISEE inferiore o uguale a 26.000 euro (<= 26.000€), DEVI specificare che rientra nella "No Tax Area" e quindi l'importo delle tasse (contributo onnicomprensivo) è ZERO. Paga solo la tassa regionale e il bollo (156 € circa totali).
           - Le scadenze delle rate vanno indicate chiaramente se richieste o previste nel bando (Solitamente 3 rate: novembre, marzo, giugno).
        
        2. LOGICA DI ORIENTAMENTO:
           - Se l'utente esprime interessi (es. robotica, informatica, costruzioni), mappa questi interessi sui Corsi presenti nel contesto e sui loro sbocchi lavorativi e dipartimenti. Sii proattivo a suggerire opzioni affini.

        Se le informazioni specifiche non sono nel contesto, scusa l'utente e consiglia di rivolgersi alla segreteria (segreteria.studenti@poliba.it).
        Formatta la risposta in Markdown chiaro con elenchi puntati se necessario.
        
        CONTESTO (Dati DB + RAG):
        {combined_context}
        
        DOMANDA STUDENTE: {query}
        """
        
        response = self.llm.invoke(system_prompt)
        return response.content
