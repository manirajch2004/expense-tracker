from flask import Flask, render_template, request, redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_2024'

DB_URL = 'postgresql://expense_tracker_db_dks7_user:EHIL3LU2EtLVecn3JMeojK5kWhJfo94J@dpg-d7le5onlk1mc73b5ns6g-a.singapore-postgres.render.com/expense_tracker_db_dks7'

def get_db():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       SERIAL PRIMARY KEY,
            name     TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id       SERIAL PRIMARY KEY,
            user_id  INTEGER NOT NULL,
            amount   REAL NOT NULL,
            category TEXT NOT NULL,
            note     TEXT,
            date     TEXT DEFAULT (CURRENT_DATE::TEXT),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']

        if not name or not email or len(password) < 6:
            return render_template('signup.html',
                                   error='Please fill all fields (password min 6 chars).')

        hashed_password = generate_password_hash(password)

        conn = get_db()
        cur  = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed_password))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Email already registered.')
        conn.close()
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip()
        password = request.form['password']

        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            return redirect('/dashboard')

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn    = get_db()
    cur     = conn.cursor()

    if request.method == 'POST':
        amount   = request.form.get('amount', 0)
        category = request.form.get('category', 'Other')
        note     = request.form.get('note', '').strip()
        try:
            amount = float(amount)
            if amount > 0:
                cur.execute(
                    "INSERT INTO expenses (user_id, amount, category, note) VALUES (%s, %s, %s, %s)",
                    (user_id, amount, category, note)
                )
                conn.commit()
        except ValueError:
            pass
        conn.close()
        return redirect('/dashboard')

    selected_category = request.args.get('category', '')

    if selected_category:
        cur.execute(
            "SELECT * FROM expenses WHERE user_id=%s AND category=%s ORDER BY id DESC",
            (user_id, selected_category)
        )
    else:
        cur.execute(
            "SELECT * FROM expenses WHERE user_id=%s ORDER BY id DESC",
            (user_id,)
        )
    expenses = cur.fetchall()

    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=%s", (user_id,))
    total = cur.fetchone()['sum'] or 0

    cur.execute("SELECT COUNT(*) FROM expenses WHERE user_id=%s", (user_id,))
    count = cur.fetchone()['count']

    cur.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=%s AND EXTRACT(MONTH FROM date::date) = EXTRACT(MONTH FROM CURRENT_DATE)",
        (user_id,)
    )
    monthly_total = cur.fetchone()['sum'] or 0

    cur.execute(
        "SELECT category, SUM(amount) as amt FROM expenses WHERE user_id=%s GROUP BY category ORDER BY amt DESC",
        (user_id,)
    )
    cat_totals = cur.fetchall()

    conn.close()

    return render_template('dashboard.html',
        expenses          = expenses,
        total             = total,
        count             = count,
        monthly_total     = monthly_total,
        cat_totals        = cat_totals,
        user_name         = session['user_name'],
        selected_category = selected_category
    )

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s",
                (expense_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

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
                    "UPDATE expenses SET amount=%s, category=%s, note=%s WHERE id=%s AND user_id=%s",
                    (amount, category, note, expense_id, session['user_id'])
                )
                conn.commit()
        except ValueError:
            pass
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM expenses WHERE id=%s AND user_id=%s",
                (expense_id, session['user_id']))
    expense = cur.fetchone()
    conn.close()

    if not expense:
        return redirect('/dashboard')

    return render_template('edit.html', expense=expense)

init_db()

if __name__ == '__main__':
    app.run(debug=True)
