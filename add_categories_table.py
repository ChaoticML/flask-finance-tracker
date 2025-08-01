import sqlite3

DATABASE_PATH = 'instance/finance.db'

def add_table():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        print("Connecting to the database...")

        # Create the 'categories' table only if it doesn't already exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        print("'categories' table created successfully (if it didn't exist).")
        
        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    add_table()