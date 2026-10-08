# Music Store Analysis — SQL Portfolio Project

A beginner-friendly SQL analysis exercise using a music-store database, invoices, customers, tracks, and related reference tables.

> **Status:** Learning/portfolio project. The SQL and import steps have not been independently executed or validated in this audit. Treat the included scripts as exercises, not production-ready database migrations.

## Topics covered

- Customers, sales, invoices, and invoice totals
- Most popular genres and artists
- Music catalog and track length
- Multi-table joins, aggregates, filtering, sorting, and subqueries

## Tools

- PostgreSQL (as referenced in the original project documentation)
- pgAdmin or another PostgreSQL SQL client
- CSV viewer/spreadsheet application for understanding the accompanying sample data

## Files in this repository

| File / group | Description |
| --- | --- |
| `Music_Store_Query.sql` | SQL queries answering music-store analysis questions |
| `Music_Store_database.sql` | Included SQL database file; encoding and import compatibility need verification |
| `Music Store- Create Tables Query.txt` | Draft table-creation definitions (known inconsistencies; see below) |
| `album.csv`, `artist.csv`, `customer.csv`, `invoice.csv`, `track.csv`, etc. | Included sample relational data |
| `schema_diagram.png`, `MusicDatabaseSchema.png` | Schema illustrations |
| `Music Store Analysis-Questions.pdf`, `SQL Music Questions2.docx` | Question/reference documents |

## Suggested local workflow

1. Create a **temporary development database** in PostgreSQL. Do not import unknown SQL scripts into a production database.
2. Inspect `Music_Store_database.sql` and the table definitions in a text editor before execution. Check encoding, table names, column types, and whether the script creates or populates tables.
3. Check the schema diagram against all supplied CSV headers.
4. Only after correcting schema inconsistencies, import CSVs into correctly structured tables in dependency order.
5. Run and verify queries from `Music_Store_Query.sql` individually.

The original repository does **not** provide a verified one-command setup process. Avoid executing all SQL files blindly.

## Known issues requiring review

- `Music Store- Create Tables Query.txt` contains an `ALTER TABLE assets` statement unrelated to the listed music tables and defines a composite table with repeated `PRIMARY KEY` declarations. It should not be treated as a ready-to-run migration.
- Some names in the query file (`invoiceline`, `miliseconds`) differ from names in the draft schema (`invoice_line`, `milliseconds`); confirm actual database schema before running the queries.
- A local fetch of `Music_Store_database.sql` failed to decode as UTF-8, so its encoding and import suitability remain unverified.
- Check provenance and license/redistribution rights of sample datasets, images, and supplied question documents before reuse.
- Verify query outputs and expected results against a known imported dataset before describing them as final analysis.

## Read-only metadata checks

The proposed draft PR adds `scripts/audit_music_store.py`, three offline unit tests and a small GitHub Actions workflow. Run locally with:

```bash
python scripts/audit_music_store.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

[GitHub Actions run #37818317051](https://github.com/29amank/Music_Store_Analysis/actions/runs/37818317051) passed all three tests and checked the expected 11 CSV headers. It reported **five existing SQL/schema warnings**, with no missing or invalid CSV-header errors:

1. `invoiceline` versus `invoice_line` naming.
2. `miliseconds` versus `milliseconds` naming.
3. An unrelated `ALTER TABLE assets` statement.
4. Duplicate primary-key declarations for `playlist_track`.
5. The draft schema treats track milliseconds as a `TIMESTAMP` rather than numeric duration.

A green audit means **the checker ran and detected these issues**, not that any existing SQL query or schema is correct, importable, or executable. No SQL was executed.

## Suggested future cleanup

- Create one canonical, validated PostgreSQL schema with correct types and keys.
- Add a reproducible, non-destructive seed/import script.
- Normalize SQL naming and check queries against the actual schema.
- Add verified example results, query explanations, and data attribution.

## License

No project license file was identified during this audit. The owner should confirm ownership and reuse rights before adding a license.
