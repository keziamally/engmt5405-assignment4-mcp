from pathlib import Path
import os
import sqlite3

from dotenv import load_dotenv


# Load configuration from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/sales.db")


def create_database() -> None:
    """Create and populate the sample sales database."""

    # Make sure the data folder exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove the old database so the script can be rerun cleanly
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Create sales table
    cursor.execute(
        """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT NOT NULL,
            units INTEGER NOT NULL,
            revenue REAL NOT NULL
        )
        """
    )

    # Fictional sample data
    sales_data = [
        ("2026-01-05", "Laptop", "Electronics", "North", 12, 14400.00),
        ("2026-01-08", "Monitor", "Electronics", "East", 20, 7000.00),
        ("2026-01-12", "Desk", "Furniture", "North", 8, 3600.00),
        ("2026-01-15", "Chair", "Furniture", "West", 25, 5000.00),
        ("2026-01-20", "Keyboard", "Electronics", "South", 30, 2100.00),
        ("2026-02-02", "Laptop", "Electronics", "East", 15, 18000.00),
        ("2026-02-06", "Mouse", "Electronics", "North", 40, 1600.00),
        ("2026-02-10", "Bookshelf", "Furniture", "South", 10, 2500.00),
        ("2026-02-14", "Monitor", "Electronics", "West", 18, 6300.00),
        ("2026-02-18", "Desk", "Furniture", "East", 11, 4950.00),
        ("2026-03-03", "Chair", "Furniture", "North", 22, 4400.00),
        ("2026-03-07", "Keyboard", "Electronics", "West", 35, 2450.00),
        ("2026-03-11", "Laptop", "Electronics", "South", 9, 10800.00),
        ("2026-03-15", "Mouse", "Electronics", "East", 50, 2000.00),
        ("2026-03-19", "Bookshelf", "Furniture", "West", 13, 3250.00),
        ("2026-04-02", "Monitor", "Electronics", "North", 16, 5600.00),
        ("2026-04-08", "Desk", "Furniture", "South", 12, 5400.00),
        ("2026-04-13", "Chair", "Furniture", "East", 28, 5600.00),
        ("2026-04-18", "Keyboard", "Electronics", "North", 45, 3150.00),
        ("2026-04-22", "Laptop", "Electronics", "West", 14, 16800.00),
    ]

    cursor.executemany(
        """
        INSERT INTO sales (
            order_date,
            product,
            category,
            region,
            units,
            revenue
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        sales_data,
    )

    connection.commit()

    # Verify how many rows were inserted
    cursor.execute("SELECT COUNT(*) FROM sales")
    row_count = cursor.fetchone()[0]

    connection.close()

    print(f"Database created successfully: {DATABASE_PATH}")
    print(f"Inserted {row_count} sales records.")


if __name__ == "__main__":
    create_database()