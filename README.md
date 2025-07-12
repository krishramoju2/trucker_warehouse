docker-compose up -d


sudo apt update && sudo apt install -y libtiff-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjpeg-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk

python create_tables.py

python -m uvicorn main:app --reload --port 8000



Here's a complete `README.md` file for your **Warehouse Management System** project with PostgreSQL, FastAPI backend, file upload, admin panel, and frontend integration:

---

### ✅ `README.md`

```markdown
# 📦 Warehouse Management System

A full-stack warehouse management application with:

- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ File/document upload & storage
- ✅ Admin panel for verification
- ✅ Frontend connected to backend via REST APIs
- ✅ Dockerized PostgreSQL setup

---

## 📁 Project Structure

```

trucker\_warehouse/
│
├── backend/
│   ├── admin/                     # Admin panel (FastAPI routes)
│   │   └── main.py
│   ├── db/                        # SQL schema (PostgreSQL)
│   │   └── schema.sql
│   ├── routers/                   # Main API routes
│   │   ├── admin.py
│   │   ├── admin\_router.py
│   │   ├── documents.py
│   │   ├── employee.py
│   │   └── models.py
│   ├── database.py                # DB connection setup
│   └── main.py                    # FastAPI app entry point
│
├── uploads/                       # Uploaded files
├── sample\_docs/                   # Sample files (optional)
├── frontend/
│   ├── index.html
│   └── script.js
│
├── docker-compose.yml             # PostgreSQL container setup
├── requirements.txt               # Python dependencies
└── README.md

````

---

## 🚀 Setup Instructions

### 1. 🐳 Start PostgreSQL via Docker

```bash
docker-compose up -d
````

### 2. 📦 Install Python packages

```bash
pip install -r requirements.txt
```

### 3. 🔥 Start Backend API (port 8080)

```bash
PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

### 4. 🛠 Start Admin Panel (port 8081)

```bash
PYTHONPATH=. uvicorn backend.admin.main:app --reload --host 0.0.0.0 --port 8081
```

---

## 📬 Example API Requests

### ➕ Create Employee

```bash
curl -X POST http://localhost:8080/employee \
-H "Content-Type: application/json" \
-d '{"name":"Krish","date_of_birth":"2000-01-01","address":"Hyderabad","contact_number":"9876543210","pan_number":"ABCDE1234F","aadhar_number":"123456789012"}'
```

### 📤 Upload Documents

```bash
curl -X POST http://localhost:8080/upload/1 \
-F "resume=@sample_docs/resume.pdf" \
-F "educational_certificates=@sample_docs/certs.pdf" \
-F "offer_letters=@sample_docs/offer.pdf" \
-F "pan_card=@sample_docs/pan.pdf" \
-F "aadhar_card=@sample_docs/aadhar.pdf" \
-F "form_16_or_it_returns=@sample_docs/form16.pdf"
```

---

## 🌐 Frontend

### Run in browser:

```bash
open frontend/index.html   # Or just open manually in browser
```

### `frontend/script.js` handles:

* Submitting employee form
* Uploading PDFs
* Fetching status

---

## 📌 Notes

* Uploaded files are saved in `/uploads/`
* PostgreSQL stores all metadata
* Admin panel is separate and can be extended
* Validations are handled using Pydantic & SQLAlchemy

---

## 📎 Requirements

* Docker & Docker Compose
* Python 3.8+
* FastAPI
* PostgreSQL
* Uvicorn

---

## 🧑‍💻 Author

Krish Ramoju
Built with ❤️ using FastAPI + PostgreSQL

```

---

Let me know if you'd like to add deployment steps (e.g., Vercel for frontend or Render for backend) or GitHub badges.
```
