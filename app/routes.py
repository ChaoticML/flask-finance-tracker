from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    entries = db.execute(
        'SELECT * FROM entries ORDER BY entry_date DESC'
    ).fetchall()
    return render_template('index.html', entries=entries)

@bp.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        # Get data from the form
        entry_date = request.form['entry_date']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        entry_type = request.form['entry_type']

        db = get_db()
        db.execute(
            'INSERT INTO entries (entry_date, description, amount, category, entry_type) VALUES (?, ?, ?, ?, ?)',
            (entry_date, description, amount, category, entry_type)
        )
        db.commit()

        return redirect(url_for('main.index'))

    # If it's a GET request, just show the form page.
    return render_template('add_entry.html')