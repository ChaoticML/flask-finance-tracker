import pandas as pd
import plotly.express as px
import plotly.io as pio

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    df = pd.read_sql_query("SELECT * FROM entries", db)

    # --- Placeholders ---
    # Good practice to define placeholders in case the dataframe is empty.
    pie_chart_html = "<p>No expense data to display a chart.</p>"
    bar_chart_html = "<p>No transaction data to display a chart.</p>"

    if df.empty:
        net_worth, total_assets, total_cash = 0, 0, 0
    else:
        # --- Calculations for Summary Cards (No changes here) ---
        net_worth = df['amount'].sum()
        total_assets = df[df['entry_type'] == 'Asset']['amount'].sum()
        total_cash = df[df['entry_type'] == 'Cash']['amount'].sum()

        # --- Pie Chart Logic (No changes here) ---
        expenses_df = df[df['amount'] < 0].copy()
        if not expenses_df.empty:
            expenses_df['amount'] = expenses_df['amount'].abs()
            fig_pie = px.pie(expenses_df, values='amount', names='category', title='Spending Breakdown')
            pie_chart_html = pio.to_html(fig_pie, full_html=False, include_plotlyjs='cdn')

        # --- NEW: Bar Chart Logic ---
        # 1. Filter for entries that are 'Bank Transaction' type.
        transactions_df = df[df['entry_type'] == 'Bank Transaction'].copy()
        if not transactions_df.empty:
            # 2. Convert 'entry_date' column to actual datetime objects for time-series analysis.
            transactions_df['entry_date'] = pd.to_datetime(transactions_df['entry_date'])

            # 3. Group by month and sum the amounts. This is the core logic.
            # 'M' stands for Month-end frequency. I set the date as the index to perform the resampling.
            monthly_data = transactions_df.set_index('entry_date').resample('M')['amount'].sum().reset_index()

            # 4. Create separate 'Income' and 'Expense' columns for clear charting.
            monthly_data['Income'] = monthly_data['amount'].clip(lower=0)
            monthly_data['Expense'] = monthly_data['amount'].clip(upper=0).abs()
            
            # Format date for cleaner labels on the chart's x-axis (e.g., "2025-Jul").
            monthly_data['entry_date'] = monthly_data['entry_date'].dt.strftime('%Y-%b')

            # 5. Create the bar chart figure.
            fig_bar = px.bar(
                monthly_data, 
                x='entry_date', 
                y=['Income', 'Expense'], 
                title='Monthly Income vs. Expense',
                barmode='group', 
                color_discrete_map={'Income': '#28a745', 'Expense': '#dc3545'} 
            )
            bar_chart_html = pio.to_html(fig_bar, full_html=False, include_plotlyjs='cdn')

    # Fetch entries for the bottom table (No changes here)
    entries = db.execute('SELECT * FROM entries ORDER BY entry_date DESC').fetchall()
    
    # Pass the bar_chart_html variable to the template
    return render_template(
        'index.html', 
        entries=entries,
        net_worth=net_worth,
        total_assets=total_assets,
        total_cash=total_cash,
        pie_chart_html=pie_chart_html,
        bar_chart_html=bar_chart_html
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