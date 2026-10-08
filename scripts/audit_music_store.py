#!/usr/bin/env python3
"""Read-only metadata audit for the Music Store SQL portfolio project.

Does NOT execute SQL, import a database, or print any CSV row data.
Warnings identify known incompatibilities without modifying source files.
"""
from collections import Counter
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "album.csv", "artist.csv", "customer.csv", "employee.csv",
    "genre.csv", "invoice.csv", "invoice_line.csv", "media_type.csv",
    "playlist.csv", "playlist_track.csv", "track.csv",
)
EXPECTED_COLUMNS = {
    "track.csv": {"track_id", "milliseconds", "bytes", "unit_price"},
    "invoice_line.csv": {"invoice_line_id", "invoice_id", "track_id", "unit_price", "quantity"},
    "customer.csv": {"customer_id", "email"},
}
QUERY_PATH = "Music_Store_Query.sql"
SCHEMA_PATH = "Music Store- Create Tables Query.txt"


def diagnostics(sql_query, schema):
    warnings = []
    if re.search(r"\binvoiceline\b", sql_query, flags=re.IGNORECASE):
        warnings.append("Query uses 'invoiceline'; supplied data uses 'invoice_line'")
    if re.search(r"\bmiliseconds\b", sql_query, flags=re.IGNORECASE):
        warnings.append("Query uses 'miliseconds'; track.csv uses 'milliseconds'")
    if re.search(r"\bALTER\s+TABLE\s+assets\b", schema, flags=re.IGNORECASE):
        warnings.append("Draft schema modifies unrelated 'assets' table")
    playlist = re.search(
        r"\bCREATE\s+TABLE\s+playlist_track\s*\((.*?)\)\s*;",
        schema, flags=re.IGNORECASE | re.DOTALL,
    )
    if playlist and len(re.findall(r"\bPRIMARY\s+KEY\b", playlist.group(1), re.IGNORECASE)) > 1:
        warnings.append("playlist_track declares more than one PRIMARY KEY")
    if re.search(r"\bmilliseconds\s+TIMESTAMP\b", schema, flags=re.IGNORECASE):
        warnings.append("Draft schema declares numeric track milliseconds as TIMESTAMP")
    return warnings


def audit(root=ROOT):
    report = {"project": "Music Store Analysis", "status": "metadata-only", "csv": {}, "warnings": [], "errors": []}
    for name in REQUIRED:
        file = root / name
        if not file.is_file():
            report["errors"].append("Missing required file: " + name)
            continue
        try:
            with file.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream)
                header = next(reader, [])
            if not header:
                report["errors"].append("Empty CSV header: " + name)
                continue
            if any(not col.strip() for col in header):
                report["errors"].append("Blank CSV header field: " + name)
            repeated = [col for col, count in Counter(header).items() if count > 1]
            if repeated:
                report["errors"].append("Repeated CSV columns in " + name + ": " + ", ".join(sorted(repeated)))
            missing = EXPECTED_COLUMNS.get(name, set()) - set(header)
            if missing:
                report["errors"].append("Expected columns missing in " + name + ": " + ", ".join(sorted(missing)))
            report["csv"][name] = {"columns": len(header), "bytes": file.stat().st_size}
        except (OSError, UnicodeError, csv.Error) as exc:
            report["errors"].append("Cannot inspect " + name + ": " + type(exc).__name__)

    try:
        queries = (root / QUERY_PATH).read_text(encoding="utf-8-sig")
        schema = (root / SCHEMA_PATH).read_text(encoding="utf-8-sig")
        report["warnings"] = diagnostics(queries, schema)
    except (OSError, UnicodeError) as exc:
        report["errors"].append("Cannot read query/schema metadata: " + type(exc).__name__)
    # Intentionally do not read or decode Music_Store_database.sql.
    return report


def main():
    report = audit()
    print(json.dumps(report, indent=2))
    # Known query/schema inconsistencies are warnings, not successful SQL tests.
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
