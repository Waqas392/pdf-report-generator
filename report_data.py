"""Stage 2: the aggregation queries. Rows in, five-ish numbers out."""
from datetime import date, timedelta

from db import get_conn

TOTALS_SQL = "SELECT COUNT(*) AS total_orders, COALESCE(SUM(amount), 0) AS total_revenue FROM orders"

TOP_PRODUCTS_SQL = """
SELECT product, COUNT(*) AS orders, ROUND(SUM(amount), 2) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC
LIMIT 5
"""

PER_DAY_SQL = """
SELECT created_at AS day, COUNT(*) AS orders
FROM orders
WHERE created_at >= ?
GROUP BY created_at
ORDER BY created_at
"""

ALL_ORDERS_SQL = "SELECT id, customer, product, amount, created_at FROM orders ORDER BY created_at DESC, id DESC"


def get_report_data() -> dict:
    conn = get_conn()
    totals = conn.execute(TOTALS_SQL).fetchone()
    top_products = [dict(r) for r in conn.execute(TOP_PRODUCTS_SQL)]

    start = date.today() - timedelta(days=6)
    found = {r["day"]: r["orders"] for r in conn.execute(PER_DAY_SQL, (start.isoformat(),))}
    # include days with zero orders so the chart/table has all 7 days
    per_day = [{"day": (start + timedelta(days=i)).isoformat(),
                "orders": found.get((start + timedelta(days=i)).isoformat(), 0)}
               for i in range(7)]

    all_orders = [dict(r) for r in conn.execute(ALL_ORDERS_SQL)]
    conn.close()
    return {
        "total_orders": totals["total_orders"],
        "total_revenue": round(totals["total_revenue"], 2),
        "top_products": top_products,
        "orders_per_day": per_day,
        "all_orders": all_orders,
    }
