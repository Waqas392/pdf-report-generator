"""Stage 3 checkpoint: render reports/test.pdf straight from the data."""
from render import render_pdf
from report_data import get_report_data

print(render_pdf(get_report_data(), "reports/test.pdf"))
