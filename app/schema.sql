-- Drop the table if it already exists to start fresh.
DROP TABLE IF EXISTS entries;

-- Create the entries table.
CREATE TABLE entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_date TEXT NOT NULL,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  entry_type TEXT NOT NULL CHECK(entry_type IN ('Bank Transaction', 'Cash', 'Asset'))
);