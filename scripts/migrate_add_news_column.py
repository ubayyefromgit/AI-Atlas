"""
Migration script: adds missing 'news_last_refreshed' column to the companies table
in the existing ai_atlas.db database.
"""
import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'database', 'ai_atlas.db'
)

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check current columns
    cur.execute("PRAGMA table_info(companies)")
    existing_cols = [row[1] for row in cur.fetchall()]
    print(f"Current companies columns: {existing_cols}")

    if 'news_last_refreshed' in existing_cols:
        print("Column 'news_last_refreshed' already exists. Nothing to do.")
        conn.close()
        return

    print("Adding 'news_last_refreshed' column...")
    cur.execute("ALTER TABLE companies ADD COLUMN news_last_refreshed DATETIME")
    conn.commit()

    # Verify
    cur.execute("PRAGMA table_info(companies)")
    new_cols = [row[1] for row in cur.fetchall()]
    print(f"Updated companies columns: {new_cols}")
    print("Migration complete!")
    conn.close()

if __name__ == "__main__":
    migrate()
