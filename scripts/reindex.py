# scripts/reindex.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- sys.path para importar rag.core ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.core import RAGSystem

# Carga .env
load_dotenv(dotenv_path=str(ROOT / ".env"))

if __name__ == "__main__":
    print("Re-indexing all documents...")
    # La inicialización ahora es mucho más simple y usa los defaults de la clase
    rag_system = RAGSystem(
        data_dir=os.getenv("DATA_DIR", "./data"),
    )
    rag_system.rebuild_index()
    print("Re-indexing complete.")
