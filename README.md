# flask-finance-tracker

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)](https://flask.palletsprojects.com/)
![Status](https://img.shields.io/badge/Status-Active%20Development-blue)

## Inspiration

Big shout-out and inspiration taken from [Tech With Tim](https://www.youtube.com/@TechWithTim).

## Description

This project is a personal finance tracker built using the Flask web framework. It allows users to log their income and expenses, categorize transactions, and visualize their financial data through interactive charts. The application uses SQLite for data storage and provides a clean, user-friendly interface.

## Features

*   **Database Integration:** Uses SQLite to store financial data, including transactions and categories.
*   **Category Management:** Allows users to create, view, and manage custom spending/income categories.
*   **Data Entry:**
    *   Add new transactions with details like date, description, amount, category, and type (income/expense).
    *   Edit existing transactions to correct errors or update information.
*   **Dashboard:**
    *   Summary cards displaying Net Worth, Total Asset Value, and Cash on Hand.
    *   Pie chart visualizing spending breakdown by category.
    *   Bar chart visualizing monthly income vs. expenses.
*   **Filtering:**
    *   Filter transactions by category and date range to analyze specific periods or spending habits.
*   **Clean and Responsive Design:** The application is designed with a modern and user-friendly interface.
*   **Git Version Control:** The project is managed using Git for version control and collaboration.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.11 or higher
*   pip (Python package installer)

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/flask-finance-tracker.git  <!-- Replace your-username -->
    cd flask-finance-tracker
    ```

2.  Create a virtual environment:

    ```bash
    python -m venv .venv
    ```

3.  Activate the virtual environment:

    *   **On Windows:**

        ```bash
        .venv\Scripts\activate
        ```

    *   **On macOS/Linux:**

        ```bash
        source .venv/bin/activate
        ```

4.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5.  Initialize the database:

    ```bash
    python add_categories_table.py
    ```

### Running the Application

```bash
python run.py
```

Open your web browser and navigate to http://127.0.0.1:5000 to access the application.
