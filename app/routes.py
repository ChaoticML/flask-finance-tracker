import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    
    # --- Filtering Logic ---
    # Get filter criteria from the URL query parameters (e.g., /?category=Food)
    selected_category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Start with a base query and an empty list for parameters
    sql = "SELECT * FROM entries WHERE 1=1"
    params = []

    if selected_category:
        sql += " AND category = ?"
        params.append(selected_category)
    if start_date:
        sql += " AND entry_date >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND entry_date <= ?"
        params.append(end_date)

    sql += " ORDER BY entry_date DESC"
    
    # Use the constructed SQL and params to fetch filtered data
    df = pd.read_sql_query(sql, db, params=tuple(params))
    
    # Fetch all categories for the filter dropdown
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    
    # --- Chart and Card Calculations (using the filtered DataFrame 'df') ---
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
                monthly_data, x='entry_date', y=['Income', 'Expense'], title='Monthly Income vs. Expense',
                barmode='group', color_discrete_map={'Income': '#28a745', 'Expense': '#dc3545'}
            )
            bar_chart_html = pio.to_html(fig_bar, full_html=False, include_plotlyjs='cdn')

    # Fetch all entries for the table (this is now redundant, but safe)
    entries = db.execute(sql, tuple(params)).fetchall()
    
    return render_template(
        'index.html', entries=entries, categories=categories,
        net_worth=net_worth, total_assets=total_assets, total_cash=total_cash,
        pie_chart_html=pie_chart_html, bar_chart_html=bar_chart_html,
        # Pass filter values back to template to keep them selected
        selected_category=selected_category, start_date=start_date, end_date=end_date
    )

# --- NEW CATEGORY MANAGEMENT ROUTE ---
@bp.route('/categories', methods=('GET', 'POST'))
def categories():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        if name:
            try:
                db.execute('INSERT INTO categories (name) VALUES (?)', (name,))
                db.commit()
            except db.IntegrityError:
                # This error occurs if the category name is not unique
                pass
        return redirect(url_for('main.categories'))

    category_list = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('categories.html', categories=category_list)

def get_entry(id):
    entry = get_db().execute('SELECT * FROM entries WHERE id = ?', (id,)).fetchone()
    if entry is None:
        abort(404, f"Entry id {id} doesn't exist.")
    return entry

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    entry = get_entry(id)
    db = get_db()

    if request.method == 'POST':
        entry_date = request.form['entry_date']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        entry_type = request.form['entry_type']

        db.execute(
            'UPDATE entries SET entry_date = ?, description = ?, amount = ?, category = ?, entry_type = ?'
            ' WHERE id = ?',
            (entry_date, description, amount, category, entry_type, id)
        )
        db.commit()
        return redirect(url_for('main.index'))

    # Fetch categories for the dropdown
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('edit_entry.html', entry=entry, categories=categories)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    get_entry(id)
    db = get_db()
    db.execute('DELETE FROM entries WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('main.index'))

@bp.route('/add', methods=('GET', 'POST'))
def add():
    db = get_db()
    if request.method == 'POST':
        entry_date = request.form['entry_date']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        entry_type = request.form['entry_type']

        db.execute(
            'INSERT INTO entries (entry_date, description, amount, category, entry_type) VALUES (?, ?, ?, ?, ?)',
            (entry_date, description, amount, category, entry_type)
        )
        db.commit()
        return redirect(url_for('main.index'))

    # Fetch categories for the dropdown
    categories = db.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('add_entry.html', categories=categories)