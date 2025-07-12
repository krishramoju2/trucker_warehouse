import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.database import SessionLocal
from backend.schema_models import EmployeeInfo  # Or models.EmployeeInfo if schema_models doesn't define it

# Load the model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create a FAISS index for 384-dim embeddings (for MiniLM model)
index = faiss.IndexFlatL2(384)
id_map = []  # Maps FAISS index to employee IDs


def build_index():
    """
    Builds the FAISS semantic index from employee data.
    """
    print("🔍 Building semantic index...")
    global id_map
    id_map.clear()
    all_embeddings = []

    db = SessionLocal()
    try:
        employees = db.query(EmployeeInfo).all()
        for emp in employees:
            combined_text = f"{emp.name} {emp.address} {emp.pan_number} {emp.aadhar_number} {emp.contact_number}"
            embedding = model.encode(combined_text)
            all_embeddings.append(embedding)
            id_map.append(emp.id)

        if all_embeddings:
            index.add(np.array(all_embeddings).astype("float32"))
            print(f"✅ Indexed {len(id_map)} employees.")
        else:
            print("⚠️ No employee records found to index.")
    except Exception as e:
        print(f"❌ Error while building index: {e}")
    finally:
        db.close()


def semantic_search(query: str, top_k=5):
    """
    Performs a semantic search over the FAISS index.
    Returns the top_k employee IDs based on query similarity.
    """
    if not id_map or index.ntotal == 0:
        print("⚠️ Index is empty. Rebuild it using build_index().")
        return []

    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding).astype("float32"), top_k)

    # Filter results to valid IDs
    results = [id_map[i] for i in I[0] if 0 <= i < len(id_map)]
    return results
