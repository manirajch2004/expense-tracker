# 💰 Expense Tracker v2 – Upgraded BCA Project

---

## ✅ WHAT'S NEW IN THIS VERSION

1. 🔐 Password Hashing   – passwords stored securely using werkzeug
2. ✏️  Edit Expense       – edit any existing expense
3. 🔍 Filter by Category – filter expenses using dropdown
4. 📊 Monthly Total      – summary card showing this month's spending
5. 🎨 UI Consistency     – edit button, filter dropdown added cleanly

---

## 🚀 HOW TO RUN

### STEP 1 – Install required libraries
Open terminal and run:
```
pip install flask werkzeug
```

### STEP 2 – ⚠️ IMPORTANT: Delete old database (MANUAL STEP)
If you used the old version before, you MUST delete the old database file.
```
Delete the file:  database.db
```
Why? Because old database has plain-text passwords.
The new version uses hashed passwords — they are not compatible.
Just delete database.db and it will be auto-created fresh when you run app.py.

### STEP 3 – Run the app
```
cd expense_tracker_v2
python app.py
```

### STEP 4 – Open in browser
```
http://127.0.0.1:5000
```

---

## 📁 PROJECT STRUCTURE

```
expense_tracker_v2/
│
├── app.py                    ← Main Flask app (all routes)
├── database.db               ← Auto-created on first run
├── README.md                 ← This file
│
├── templates/
│   ├── login.html            ← Login page
│   ├── signup.html           ← Signup page
│   ├── dashboard.html        ← Main dashboard (UPDATED)
│   └── edit.html             ← NEW: Edit expense page
│
└── static/
    ├── css/
    │   └── style.css         ← All styles (UPDATED)
    └── js/
        └── script.js         ← Animations & confirmations
```

---

## ⚠️ MANUAL STEPS SUMMARY

| Step | What to do manually | Why |
|------|--------------------|----|
| 1 | pip install flask werkzeug | Install libraries |
| 2 | Delete old database.db | Old passwords are plain text, not compatible |
| 3 | Create new account (signup) | Old accounts won't work after password change |
| 4 | python app.py | Run the app |

---

## 🔐 PASSWORD SECURITY EXPLAINED (for viva)

Old version:
- Password stored as: "mypassword123"  ← anyone can read it

New version:
- Password stored as: "pbkdf2:sha256:600000$abc123..." ← hashed, unreadable
- generate_password_hash() → converts password to hash during signup
- check_password_hash()    → verifies password during login

---

## 🎓 BCA Final Year Project
Student  : Maniraj Chauhan
College  : Radha Govind University, Ramgarh
Session  : 2023–2026
