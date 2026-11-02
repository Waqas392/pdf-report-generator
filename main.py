"""Stages 0, 4, 5: the API. Pipeline runs inside the endpoint (no background jobs)."""
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from db import get_conn
from render import render_pdf
from report_data import get_report_data

REPORTS_DIR = Path(__file__).parent / "reports"
app = FastAPI(title="PDF report generator")


def _record(row) -> dict:
    return {"id": row["id"], "created_at": row["created_at"], "file": f"/reports/{row['id']}/file"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
def create_report():
    conn = get_conn()
    try:
        cur = conn.execute("INSERT INTO reports (created_at) VALUES (?)",
                           (datetime.now().isoformat(timespec="seconds"),))
        report_id = cur.lastrowid
        path = REPORTS_DIR / f"{report_id}.pdf"
        try:
            render_pdf(get_report_data(), path)
        except Exception:
            conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            conn.commit()
            raise
        conn.execute("UPDATE reports SET path = ? WHERE id = ?", (str(path), report_id))
        conn.commit()
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        return _record(row)
    finally:
        conn.close()
@app.get("/reports")
def list_reports():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM reports WHERE path IS NOT NULL ORDER BY id DESC").fetchall()
    conn.close()
    return [_record(r) for r in rows]


def _get_or_404(report_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM reports WHERE id = ? AND path IS NOT NULL", (report_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return row


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    return _record(_get_or_404(report_id))


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    row = _get_or_404(report_id)
    if not Path(row["path"]).exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(row["path"], media_type="application/pdf",
                        filename=f"sales-report-{row['created_at'][:10]}-{row['id']}.pdf")
