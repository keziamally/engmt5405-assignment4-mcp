from pathlib import Path
import os
import sqlite3
from typing import Any

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "data/sales.db")

ALLOWED_GROUP_BY = {"region", "category", "product"}


def get_connection() -> sqlite3.Connection:
    """
    Create a SQLite connection that returns rows like dictionaries.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def filter_sales(
    region: str | None = None,
    category: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Return sales records filtered by optional region and category.

    Uses parameterized SQL to avoid SQL injection.
    """

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    query = """
        SELECT
            id,
            order_date,
            product,
            category,
            region,
            units,
            revenue
        FROM sales
        WHERE 1 = 1
    """

    parameters: list[Any] = []

    if region:
        query += " AND region = ?"
        parameters.append(region)

    if category:
        query += " AND category = ?"
        parameters.append(category)

    query += " ORDER BY order_date ASC LIMIT ?"
    parameters.append(limit)

    connection = get_connection()

    try:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def summarize_sales(group_by: str = "region") -> list[dict[str, Any]]:
    """
    Return aggregate sales totals grouped by region, category, or product.
    """

    if group_by not in ALLOWED_GROUP_BY:
        allowed = ", ".join(sorted(ALLOWED_GROUP_BY))
        raise ValueError(
            f"Invalid group_by value. Allowed values: {allowed}"
        )

    query = f"""
        SELECT
            {group_by} AS group_name,
            SUM(units) AS total_units,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY {group_by}
        ORDER BY total_revenue DESC
    """

    connection = get_connection()

    try:
        rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()