"""Stage 2 checkpoint: print the report object as JSON (all_orders trimmed)."""
import json
from report_data import get_report_data

data = get_report_data()
preview = {**data, "all_orders": f"<{len(data['all_orders'])} rows>"}
print(json.dumps(preview, indent=2))
assert data["top_products"][0]["revenue"] <= data["total_revenue"]
