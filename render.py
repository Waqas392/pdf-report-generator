"""Stage 3: numbers -> HTML -> PDF (headless Chromium via Playwright)."""
from datetime import date
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright

CSS = """
@page { size: A4; margin: 18mm 14mm 20mm; }
* { box-sizing: border-box; }
body { font-family: Helvetica, Arial, sans-serif; color: #1f2937; font-size: 11px; }
header { border-bottom: 3px solid #4f46e5; padding-bottom: 8px; margin-bottom: 18px; }
h1 { margin: 0; font-size: 24px; color: #4f46e5; }
.sub { color: #6b7280; margin-top: 4px; }
h2 { font-size: 14px; margin: 22px 0 8px; color: #111827; }
.kpis { display: flex; gap: 14px; }
.kpi { flex: 1; background: #eef2ff; border-radius: 8px; padding: 12px 14px; }
.kpi .v { font-size: 22px; font-weight: 700; color: #4338ca; }
.kpi .l { color: #6b7280; text-transform: uppercase; font-size: 9px; letter-spacing: .05em; }
table { width: 100%; border-collapse: collapse; }
th { background: #4f46e5; color: #fff; text-align: left; padding: 6px 8px; }
td { padding: 5px 8px; border-bottom: 1px solid #e5e7eb; }
tbody tr:nth-child(even) td { background: #f9fafb; }
td.num, th.num { text-align: right; }
thead { display: table-header-group; }   /* repeat header on every page */
tr { break-inside: avoid; }              /* never slice a row in half */
"""


def _table(headers, rows, num_cols=()):
    head = "".join(f'<th class="{"num" if i in num_cols else ""}">{escape(h)}</th>'
                   for i, h in enumerate(headers))
    body = "".join(
        "<tr>" + "".join(f'<td class="{"num" if i in num_cols else ""}">{escape(str(c))}</td>'
                         for i, c in enumerate(r)) + "</tr>"
        for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def build_html(data: dict) -> str:
    top = _table(["Product", "Orders", "Revenue ($)"],
                 [(p["product"], p["orders"], f'{p["revenue"]:,.2f}') for p in data["top_products"]],
                 num_cols=(1, 2))
    per_day = _table(["Day", "Orders"],
                     [(d["day"], d["orders"]) for d in data["orders_per_day"]], num_cols=(1,))
    all_orders = _table(["ID", "Customer", "Product", "Amount ($)", "Date"],
                        [(o["id"], o["customer"], o["product"], f'{o["amount"]:,.2f}', o["created_at"])
                         for o in data["all_orders"]], num_cols=(0, 3))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<header><h1>Sales Report</h1><div class="sub">Generated {date.today():%d %B %Y}</div></header>
<div class="kpis">
  <div class="kpi"><div class="v">{data["total_orders"]:,}</div><div class="l">Total orders</div></div>
  <div class="kpi"><div class="v">${data["total_revenue"]:,.2f}</div><div class="l">Total revenue</div></div>
</div>
<h2>Top 5 products by revenue</h2>{top}
<h2>Orders per day (last 7 days)</h2>{per_day}
<h2>All orders</h2>{all_orders}
</body></html>"""


def render_pdf(data: dict, out_path: Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(data)
    footer = ('<div style="width:100%;font-size:8px;color:#9ca3af;text-align:center;">'
              'Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=str(out_path), format="A4", print_background=True,
                 display_header_footer=True, header_template="<span></span>",
                 footer_template=footer)
        browser.close()
    return out_path
