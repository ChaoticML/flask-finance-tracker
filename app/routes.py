import pandas as pd
import plotly.express as px
import plotly.io as pio

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    
    # Use pandas to read all data from the database into a DataFrame.
    df = pd.read_sql_query("SELECT * FROM entries", db)

    # --- Calculations for Summary Cards ---
    if df.empty:
        net_worth = 0
        total_assets = 0
        total_cash = 0
        pie_chart_html = "<p>No expense data yet to create a chart.</p>"
    else:
        net_worth = df['amount'].sum()
        total_assets = df[df['entry_type'] == 'Asset']['amount'].sum()
        total_cash = df[df['entry_type'] == 'Cash']['amount'].sum()

        # --- Chart Generation: Expenses by Category ---
        expenses_df = df[df['amount'] < 0].copy()
        
        if not expenses_df.empty:
            expenses_df['amount'] = expenses_df['amount'].abs()
            
            fig_pie = px.pie(
                expenses_df, 
                values='amount', 
                names='category', 
                title='Expenses by Category'
            )
            pie_chart_html = pio.to_html(fig_pie, full_html=False, include_plotlyjs='cdn')
        else:
            pie_chart_html = "<p>No expense data yet to create a chart.</p>"
    entries = db.execute(
        'SELECT * FROM entries ORDER BY entry_date DESC'
    ).fetchall()
    
    return render_template(
        'index.html', 
        entries=entries,
        net_worth=net_worth,
        total_assets=total_assets,
        total_cash=total_cash,
        pie_chart_html=pie_chart_html
    )


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