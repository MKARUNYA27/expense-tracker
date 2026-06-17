from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- HOME PAGE ----------
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = c.fetchall()
    conn.close()

    total_income = 0
    total_expense = 0
    for t in transactions:
        if t[1] > 0:
            total_income += t[1]
        else:
            total_expense += abs(t[1])

    balance = total_income - total_expense

    return render_template('index.html', 
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance)

# ---------- ADD TRANSACTION ----------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        transaction_type = request.form['type']
        if transaction_type == 'expense':
            amount = -amount  # Make negative for expenses
        category = request.form['category']
        description = request.form['description']
        date = request.form['date']

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('INSERT INTO transactions (amount, category, description, date) VALUES (?, ?, ?, ?)',
                  (amount, category, description, date))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add.html')

# ---------- DELETE TRANSACTION ----------
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
