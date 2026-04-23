from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_2024'

DB = 'database.db'

# ── Helper: get DB connection ─────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ── Auto-create tables on first run ──────────────────────────────
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            amount   REAL NOT NULL,
            category TEXT NOT NULL,
            note     TEXT,
            date     TEXT DEFAULT (DATE('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ── Home ──────────────────────────────────────────────────────────
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# ── Signup ────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        if not name or not email or len(password) < 6:
            return render_template('signup.html',
                                   error='Please fill all fields (password min 6 chars).')

        # ✅ IMPROVEMENT 1: Hash the password before saving
        hashed_password = generate_password_hash(password)

        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        (name, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Email already registered.')
        conn.close()
        return redirect('/login')

    return render_template('signup.html')

# ── Login ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']

        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        # ✅ IMPROVEMENT 1: Check hashed password
        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            return redirect('/dashboard')

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')

# ── Logout ────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ── Dashboard ─────────────────────────────────────────────────────
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn    = get_db()
    cur     = conn.cursor()

    # Add new expense
    if request.method == 'POST':
        amount   = request.form.get('amount', 0)
        category = request.form.get('category', 'Other')
        note     = request.form.get('note', '').strip()
        try:
            amount = float(amount)
            if amount > 0:
                cur.execute(
                    "INSERT INTO expenses (user_id, amount, category, note) VALUES (?, ?, ?, ?)",
                    (user_id, amount, category, note)
                )
                conn.commit()
        except ValueError:
            pass
        conn.close()
        return redirect('/dashboard')

    # ✅ IMPROVEMENT 3: Filter by category (GET parameter)
    selected_category = request.args.get('category', '')

    if selected_category:
        cur.execute(
            "SELECT * FROM expenses WHERE user_id=? AND category=? ORDER BY id DESC",
            (user_id, selected_category)
        )
    else:
        cur.execute(
            "SELECT * FROM expenses WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        )
    expenses = cur.fetchall()

    # Total of all expenses
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    total = cur.fetchone()[0] or 0

    # Count of all expenses
    cur.execute("SELECT COUNT(*) FROM expenses WHERE user_id=?", (user_id,))
    count = cur.fetchone()[0]

    # ✅ IMPROVEMENT 4: Monthly total using strftime
    cur.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=? AND strftime('%m', date) = strftime('%m', 'now')",
        (user_id,)
    )
    monthly_total = cur.fetchone()[0] or 0

    # Category totals for bar chart
    cur.execute(
        "SELECT category, SUM(amount) as amt FROM expenses WHERE user_id=? GROUP BY category ORDER BY amt DESC",
        (user_id,)
    )
    cat_totals = cur.fetchall()

    conn.close()

    return render_template('dashboard.html',
        expenses         = expenses,
        total            = total,
        count            = count,
        monthly_total    = monthly_total,
        cat_totals       = cat_totals,
        user_name        = session['user_name'],
        selected_category= selected_category
    )

# ── Delete Expense ────────────────────────────────────────────────
@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=? AND user_id=?",
                (expense_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

# ── Edit Expense ─────────────────────────────────────────────────
# ✅ IMPROVEMENT 2: New edit route
@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur  = conn.cursor()

    if request.method == 'POST':
        amount   = request.form.get('amount', 0)
        category = request.form.get('category', 'Other')
        note     = request.form.get('note', '').strip()
        try:
            amount = float(amount)
            if amount > 0:
                cur.execute(
                    "UPDATE expenses SET amount=?, category=?, note=? WHERE id=? AND user_id=?",
                    (amount, category, note, expense_id, session['user_id'])
                )
                conn.commit()
        except ValueError:
            pass
        conn.close()
        return redirect('/dashboard')

    # GET: load existing expense data into form
    cur.execute("SELECT * FROM expenses WHERE id=? AND user_id=?",
                (expense_id, session['user_id']))
    expense = cur.fetchone()
    conn.close()

    if not expense:
        return redirect('/dashboard')

    return render_template('edit.html', expense=expense)

# This runs init_db when app starts on Render too
init_db()

if __name__ == '__main__':
    app.run(debug=True)
