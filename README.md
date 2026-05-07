# 🩸 BloodLink — Blood Donation System
**DBMS Project | Flask + MySQL | PL/SQL: Procedures · Functions · Cursors · Triggers**

---

## ✅ PL/SQL Components Covered

| Requirement  | File                    | Name                        |
|-------------|-------------------------|-----------------------------|
| **Procedure** | `04_procedures.sql`    | `find_donors(bg, city)`     |
| **Cursor**    | `04_procedures.sql`    | `get_blood_group_stats()`   |
| **Function**  | `03_function.sql`      | `fn_days_since_donation(id)`|
| **Trigger**   | `05_trigger.sql`       | `trg_check_availability`    |

---

## ⚡ Setup in 5 Steps

### Step 1 — Install Python packages
```bash
pip install flask mysql-connector-python
```

### Step 2 — Run SQL files IN ORDER (in MySQL Workbench or CLI)
```
01_create_db.sql        → Creates the database
02_create_tables.sql    → Creates donors & requests tables
03_function.sql         → Creates fn_days_since_donation()
04_procedures.sql       → Creates find_donors() + get_blood_group_stats()
05_trigger.sql          → Creates trg_check_availability
06_sample_data.sql      → Inserts test data
```

Via CLI:
```bash
mysql -u root -p < data/01_create_db.sql
mysql -u root -p < data/02_create_tables.sql
mysql -u root -p < data/03_function.sql
mysql -u root -p < data/04_procedures.sql
mysql -u root -p < data/05_trigger.sql
mysql -u root -p < data/06_sample_data.sql
```

### Step 3 — Set your MySQL password in app.py
```python
DB_CONFIG = {
    "password": "your_password_here",   # ← change this
    ...
}
```

### Step 4 — Run Flask
```bash
python app.py
```

### Step 5 — Open browser
```
http://127.0.0.1:5000
```

---

## 🗂 Project Structure
```
blood_donation_project/
├── app.py                     ← Flask backend
├── data/
│   ├── 01_create_db.sql
│   ├── 02_create_tables.sql
│   ├── 03_function.sql        ← fn_days_since_donation()
│   ├── 04_procedures.sql      ← find_donors() + get_blood_group_stats() [CURSOR]
│   ├── 05_trigger.sql         ← trg_check_availability
│   └── 06_sample_data.sql
└── templates/
    └── index.html             ← Frontend UI
```

---

## 📌 How Each PL/SQL Component is Used

| Component | What it does | Where triggered |
|-----------|-------------|-----------------|
| `fn_days_since_donation(id)` | Returns days since donor's last donation | Dashboard table, Search results |
| `find_donors(bg, city)` | Selects available donors for a blood group + city | Find Donor tab → Search button |
| `get_blood_group_stats()` | Uses a **CURSOR** to build availability stats per blood group | Dashboard → blood group cards |
| `trg_check_availability` | Auto-sets `is_available` on every UPDATE to donors | Fires on any donor record update |
