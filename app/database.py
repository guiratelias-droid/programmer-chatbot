"""
database.py — the ONLY place that talks to the database.

Every feature that needs data goes through here.
"""

import sqlite3

from app.config import settings


def get_connection():
    """Open a connection to our SQLite file."""
    connection = sqlite3.connect(settings.db_path)
    # Make each row behave like a dictionary: row["name"] instead of row[0].
    connection.row_factory = sqlite3.Row
    return connection


def run_select(query: str):
    """
    Run a read-only SELECT query and return a list of dictionaries.
    Always close the connection, even if something goes wrong.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()