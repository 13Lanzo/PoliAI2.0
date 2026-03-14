import os
import chromadb
from dotenv import load_dotenv

# Nota: per chunking avanzato useremo librerie specializzate come langchain o PyMuPDF.
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 1. Caricamento variabili d'ambiente (per GOOGLE_API_KEY)
load_dotenv()

# ==========================================
# CONFIGURAZIONE PERCORSI MODULARE
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DOCS_DIR = os.path.join(DATA_DIR, 'raw_documents')
CHROMA_DB_DIR = os.path.join(DATA_DIR, 'chroma_db')

# Assicuriamoci che le directory esistano
os.makedirs(RAW_DOCS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# ==========================================
# INIZIALIZZAZIONE CHROMADB & GEMINI
# ==========================================
# Inizializziamo il client Chroma Persistent per salvare i vettori su disco
print(f"[*] Inizializzando ChromaDB in: {CHROMA_DB_DIR}")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

# Utilizziamo Gemini flash o modelli specifici per l'embedding
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def get_or_create_collection(collection_name="polibai_docs"):
    """Recupera o crea una nuova collection in ChromaDB"""
    try:
        # Recuperiamo la collection. Usiamo similarità coseno (cosine)
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        return collection
    except Exception as e:
        print(f"[ERROR] Impossibile creare/recuperare la collection: {e}")
        return None

def process_and_ingest_pdf(file_path, collection, source_name):
    """Estrae il testo, divide in chunk e fa l'ingestion."""
    print(f"\n[*] Processando documento: {source_name}...")
    
    # A. Estrazione del testo dal file PDF
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
    except Exception as e:
        print(f"[ERROR] Impossibile leggere il PDF {source_name}: {e}")
        return

    # B. Chunking Semantico
    # Parametri ottimizzati per bandi con commi e paragrafi lunghi
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> Creati {len(chunks)} chunk dal documento.")
    
    if not chunks:
        print("  -> Nessun testo utile trovato. Skip.")
        return

    # C. Preparazione liste per ChromaDB
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [{"source": source_name, "page": chunk.metadata.get("page", 0)} for chunk in chunks]
    ids = [f"{source_name}_chunk_{i}" for i in range(len(chunks))]
    
    # D. Calcolo Embeddings (Gemini) e Salvataggio (Chroma)
    print("  -> Calcolo degli embeddings tramite Google Gemini...")
    try:
        # Se GoogleGenerativeAIEmbeddings fa rate-limit, andrà gestito a lotti
        embeddings = gemini_embeddings.embed_documents(texts)
        
        print("  -> Salvataggio nel Vector Database...")
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[OK] Documento {source_name} indicizzato correttamente!")
    except Exception as e:
        print(f"[ERROR] Durante l'embedding/salvataggio: {e}")

def main():
    print("=== PolibAI 2.0 Ingestion Pipeline ===")
    collection = get_or_create_collection()
    if not collection:
        return
        
    pdf_files = [f for f in os.listdir(RAW_DOCS_DIR) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"[!] Nessun file PDF trovato in: {RAW_DOCS_DIR}")
        print("[!] Inserisci il 'Bando Erasmus+ 2026/2027.pdf' o il 'Regolamento Tasse.pdf' ed esegui nuovamente lo script.")
        return
        
    for pdf_file in pdf_files:
        file_path = os.path.join(RAW_DOCS_DIR, pdf_file)
        process_and_ingest_pdf(file_path, collection, source_name=pdf_file)
        
    print("\n=== Ingestion completata! ===")

if __name__ == "__main__":
    main()
