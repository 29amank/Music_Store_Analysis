"""Offline tests for read-only music-store file and SQL metadata checks."""
from pathlib import Path
import tempfile
import unittest

from scripts.audit_music_store import (
    EXPECTED_COLUMNS, REQUIRED, QUERY_PATH, SCHEMA_PATH, audit, diagnostics,
)


class TestMusicStoreAudit(unittest.TestCase):
    def test_known_source_warnings_detected(self):
        result = audit()
        self.assertEqual(result["status"], "metadata-only")
        self.assertIn("track.csv", result["csv"])
        self.assertEqual(len(result["csv"]), len(REQUIRED))
        joined = "\n".join(result["warnings"])
        self.assertIn("invoiceline", joined)
        self.assertIn("miliseconds", joined)
        self.assertIn("playlist_track", joined)
        self.assertIn("assets", joined)
        # This tests detection, not whether SQL is executable.

    def test_known_sql_issues_are_detected_without_database(self):
        issues = diagnostics(
            "SELECT miliseconds FROM track JOIN invoiceline ON true",
            "ALTER TABLE assets ADD COLUMN dummy INTEGER; "
            "CREATE TABLE playlist_track (id int PRIMARY KEY, name text PRIMARY KEY); "
            "CREATE TABLE track (milliseconds TIMESTAMP);",
        )
        self.assertEqual(len(issues), 5)

    def test_synthetic_archive_is_read_only_and_has_no_rows_printed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in REQUIRED:
                headers = sorted(EXPECTED_COLUMNS.get(name, {"id"}))
                (root / name).write_text(",".join(headers) + "\nsynthetic", encoding="utf-8")
            (root / QUERY_PATH).write_text("SELECT * FROM track;", encoding="utf-8")
            (root / SCHEMA_PATH).write_text("CREATE TABLE track (id INT);", encoding="utf-8")
            snapshot = {p.name: p.read_bytes() for p in root.iterdir()}
            result = audit(root)
            self.assertFalse(result["errors"], result["errors"])
            self.assertFalse(result["warnings"], result["warnings"])
            self.assertEqual(snapshot, {p.name: p.read_bytes() for p in root.iterdir()})
            self.assertNotIn("synthetic", str(result))


if __name__ == "__main__":
    unittest.main()
