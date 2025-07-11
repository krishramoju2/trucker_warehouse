import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.database import SessionLocal
from backend.models import EmployeeInfo, DocumentInfo  # adjust to your actual model names

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.IndexFlatL2(384)  # embedding size for the model

id_map = []  # maps FAISS index to employee ID

def build_index():
    db = SessionLocal()
    global id_map
    all_embeddings = []
    id_map = []

    employees = db.query(EmployeeInfo).all()
    for emp in employees:
        text = f"{emp.name} {emp.address} {emp.pan_number} {emp.aadhar_number} {emp.contact_number}"
        emb = model.encode(text)
        all_embeddings.append(emb)
        id_map.append(emp.id)

    if all_embeddings:
        index.add(np.array(all_embeddings).astype("float32"))

def semantic_search(query: str, top_k=5):
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb).astype("float32"), top_k)
    results = [id_map[i] for i in I[0] if i < len(id_map)]
    return results
