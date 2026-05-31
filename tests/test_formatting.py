import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".py", ".csv", ".md", ".json", ".yml", ".yaml"}
SKIP_PARTS = {".git", "__pycache__", ".matplotlib_cache", ".ipynb_checkpoints"}


def project_text_files():
    for file_path in PROJECT_ROOT.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in SKIP_PARTS for part in file_path.parts):
            continue
        if file_path.suffix.lower() in TEXT_EXTENSIONS:
            yield file_path


class FormattingTest(unittest.TestCase):
    def test_large_text_files_are_not_compressed_into_one_line(self):
        for file_path in project_text_files():
            text = file_path.read_text(encoding="utf-8")
            if len(text) > 200:
                self.assertGreater(
                    text.count("\n"),
                    1,
                    f"{file_path} appears to be compressed into one line.",
                )

    def test_json_files_are_valid(self):
        for file_path in PROJECT_ROOT.rglob("*.json"):
            if any(part in SKIP_PARTS for part in file_path.parts):
                continue
            with file_path.open(encoding="utf-8") as file:
                json.load(file)

    def test_csv_files_have_header_and_records_on_separate_lines(self):
        for file_path in (PROJECT_ROOT / "data").rglob("*.csv"):
            lines = file_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertGreaterEqual(len(lines), 2, f"{file_path} needs records.")
            self.assertIn(",", lines[0], f"{file_path} needs a CSV header.")


if __name__ == "__main__":
    unittest.main()
