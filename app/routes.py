import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    df = pd.read_sql_query("SELECT * FROM entries", db)

    pie_chart_html = "<p>No expense data to display a chart.</p>"
    bar_chart_html = "<p>No transaction data to display a chart.</p>"

    if df.empty:
        net_worth, total_assets, total_cash = 0, 0, 0
    else:
        net_worth = df['amount'].sum()
        total_assets = df[df['entry_type'] == 'Asset']['amount'].sum()
        total_cash = df[df['entry_type'] == 'Cash']['amount'].sum()

        expenses_df = df[df['amount'] < 0].copy()
        if not expenses_df.empty:
            expenses_df['amount'] = expenses_df['amount'].abs()
            fig_pie = px.pie(expenses_df, values='amount', names='category', title='Spending Breakdown')
            pie_chart_html = pio.to_html(fig_pie, full_html=False, include_plotlyjs='cdn')

        transactions_df = df[df['entry_type'] == 'Bank Transaction'].copy()
        if not transactions_df.empty:
            transactions_df['entry_date'] = pd.to_datetime(transactions_df['entry_date'])
            monthly_data = transactions_df.set_index('entry_date').resample('ME')['amount'].sum().reset_index()
            monthly_data['Income'] = monthly_data['amount'].clip(lower=0)
            monthly_data['Expense'] = monthly_data['amount'].clip(upper=0).abs()
            monthly_data['entry_date'] = monthly_data['entry_date'].dt.strftime('%Y-%b')
            fig_bar = px.bar(
                monthly_data, 
                x='entry_date', 
                y=['Income', 'Expense'], 
                title='Monthly Income vs. Expense',
                barmode='group',
                color_discrete_map={'Income': '#28a745', 'Expense': '#dc3545'}
            )
            bar_chart_html = pio.to_html(fig_bar, full_html=False, include_plotlyjs='cdn')

    entries = db.execute('SELECT * FROM entries ORDER BY entry_date DESC').fetchall()
    
    return render_template(
        'index.html', 
        entries=entries,
        net_worth=net_worth,
        total_assets=total_assets,
        total_cash=total_cash,
        pie_chart_html=pie_chart_html,
        bar_chart_html=bar_chart_html
    )

def get_entry(id):
    """Get a single entry by its ID."""
    entry = get_db().execute(
        'SELECT * FROM entries WHERE id = ?', (id,)
    ).fetchone()
    
    if entry is None:
        abort(404, f"Entry id {id} doesn't exist.")
        
    return entry

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    entry = get_entry(id)

    if request.method == 'POST':
        entry_date = request.form['entry_date']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        entry_type = request.form['entry_type']

        db = get_db()
        db.execute(
            'UPDATE entries SET entry_date = ?, description = ?, amount = ?, category = ?, entry_type = ?'
            ' WHERE id = ?',
            (entry_date, description, amount, category, entry_type, id)
        )
        db.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_entry.html', entry=entry)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    get_entry(id)
    db = get_db()
    db.execute('DELETE FROM entries WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main.index'))

@bp.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
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

    return render_template('add_entry.html')