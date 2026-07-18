# backend/services/ingestion/report.py
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("ingestion")

class ImportReport:
    def __init__(self):
        self.stats = {
            "companies": {"imported": 0, "updated": 0, "skipped": 0},
            "problems": {"imported": 0, "updated": 0, "skipped": 0},
            "sectors": {"imported": 0, "updated": 0, "skipped": 0},
            "mappings": {"imported": 0, "updated": 0, "skipped": 0},
        }
        self.warnings = 0
        self.errors = 0
        self.duration_seconds = 0.0

    def add_warning(self):
        self.warnings += 1

    def add_error(self):
        self.errors += 1

    def increment(self, table: str, action: str):
        if table in self.stats and action in self.stats[table]:
            self.stats[table][action] += 1

    def generate_console_summary(self):
        print("\n==========================")
        print(" AI Atlas Import Summary")
        print("==========================\n")
        
        for table, counts in self.stats.items():
            print(f"{table.capitalize()}")
            print(f"Imported: {counts['imported']}")
            print(f"Updated: {counts['updated']}")
            print(f"Skipped: {counts['skipped']}\n")

        print(f"Warnings: {self.warnings}")
        print(f"Errors: {self.errors}")
        print(f"Duration: {self.duration_seconds:.2f}s\n")
        print("==========================")

    def write_json_summary(self, filepath: str):
        data = {
            "stats": self.stats,
            "warnings": self.warnings,
            "errors": self.errors,
            "duration": self.duration_seconds
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Wrote import summary JSON to {filepath}")
