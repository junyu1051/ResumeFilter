# 🧠 Resume Management System

**FastAPI-based resume management backend**
---

## 🚀 Quick Start

### 1️⃣ Clone the repo

### 2️⃣ Set up a virtual environment
**Windows:**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

If you get `email_validator` errors:
```bash
pip install email-validator
```

---

### 4️⃣ Configure environment variables

Create a `.env` file in the project root:
```
DATABASE_URL=mysql+pymysql://root:<YOUR_PASSWORD>@localhost:3306/resume_system
JWT_SECRET=super_secret_key
JWT_ALGORITHM=HS256
```

💡 **Make sure the database exists!**
If not, create it manually in MySQL:
```sql
CREATE DATABASE resume_system CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

---

### 5️⃣ Launch the FastAPI app
```bash
uvicorn app.main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

---

## 🧹 Notes 

- Don’t push your `.venv` — it’s in `.gitignore` for a reason.  
- Don’t commit `.env` either — that’s how you leak passwords.  
- Use `pip freeze > requirements.txt` if you install new packages.  
- Always run `git pull` before you start editing — don’t be *that* guy.

---

## 🧨 Common errors

| Error | Cause | Fix |
|-------|--------|-----|
| `Unknown database 'resume_system'` | You didn’t create the DB | `CREATE DATABASE resume_system;` |
| `email-validator not installed` | Missing dependency | `pip install email-validator` |
| `401 Unauthorized` | Wrong password or not registered | Register first |
| `ModuleNotFoundError: No module named 'app'` | You ran from wrong directory | Run `uvicorn app.main:app --reload` from project root |
