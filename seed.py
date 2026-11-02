"""Seed report.db with ~200 random orders. Safe to run twice: it wipes first."""
import random
from datetime import date, timedelta

from db import get_conn

PRODUCTS = ["Laptop Stand", "Mechanical Keyboard", "USB-C Hub",
            "Noise-Cancelling Headphones", "Webcam HD", "Desk Lamp"]
CUSTOMERS = ["Ali", "Sara", "Usman", "Ayesha", "Bilal", "Hina", "Zain",
             "Maryam", "Hamza", "Noor", "Fatima", "Omar", "Iqra", "Danish"]


def seed(n: int = 200) -> None:
    random.seed(42)  # reproducible dev data
    today = date.today()
    rows = [
        (random.choice(CUSTOMERS), random.choice(PRODUCTS),
         round(random.uniform(5, 200), 2),
         (today - timedelta(days=random.randint(0, 29))).isoformat())
        for _ in range(n)
    ]
    conn = get_conn()
    with conn:
        conn.execute("DELETE FROM orders")  # idempotent: one clean copy
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'orders'")  # ids restart at 1
        conn.executemany(
            "INSERT INTO orders (customer, product, amount, created_at) VALUES (?,?,?,?)",
            rows)
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"orders in db: {count}")


if __name__ == "__main__":
    seed()
