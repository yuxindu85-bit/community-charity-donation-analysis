import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".py", ".csv", ".md", ".json", ".yml", ".yaml"}
SKIP_PARTS = {".git", "__pycache__", ".matplotlib_cache", ".ipynb_checkpoints"}

IMPORTANT_PYTHON_FILES = [
    "src/utils.py",
    "src/clean_data.py",
    "src/analyze_donations.py",
    "src/analyze_inventory.py",
    "src/analyze_sales.py",
    "src/analyze_booth_layout.py",
    "src/create_charts.py",
    "src/model_utils.py",
    "src/train_price_model.py",
    "src/train_sale_success_model.py",
    "src/run_all.py",
    "dashboard/app.py",
    "tests/test_clean_data.py",
    "tests/test_analysis.py",
    "tests/test_outputs.py",
    "tests/test_privacy.py",
    "tests/test_formatting.py",
]

IMPORTANT_CSV_FILES = [
    "data/raw/donation_records_sample.csv",
    "data/raw/item_inventory_sample.csv",
    "data/raw/sale_records_sample.csv",
    "data/processed/cleaned_donations.csv",
    "data/processed/cleaned_inventory.csv",
    "data/processed/cleaned_sales.csv",
    "data/processed/merged_event_data.csv",
]

IMPORTANT_MARKDOWN_FILES = [
    "README.md",
    "docs/project_background.md",
    "docs/data_dictionary.md",
    "docs/workflow_notes.md",
    "docs/data_privacy_note.md",
    "docs/methodology.md",
    "docs/limitations.md",
    "docs/reflection.md",
    "docs/future_improvements.md",
    "reports/final_charity_sale_report.md",
    "reports/event_operation_review.md",
    "reports/model_report.md",
]


def project_text_files():
    for file_path in PROJECT_ROOT.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in SKIP_PARTS for part in file_path.parts):
            continue
        if file_path.suffix.lower() in TEXT_EXTENSIONS:
            yield file_path


class FormattingTest(unittest.TestCase):
    def test_readme_has_enough_normal_lines(self):
        readme_lines = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(readme_lines), 100)

    def test_important_python_files_have_normal_line_counts(self):
        for relative_path in IMPORTANT_PYTHON_FILES:
            lines = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8").splitlines()
            self.assertGreater(
                len(lines),
                30,
                f"{relative_path} should not be compressed into a few lines.",
            )

    def test_important_csv_files_have_normal_line_counts(self):
        for relative_path in IMPORTANT_CSV_FILES:
            lines = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8").splitlines()
            self.assertGreater(
                len(lines),
                10,
                f"{relative_path} should have one record per line.",
            )

    def test_important_markdown_files_have_normal_line_counts(self):
        for relative_path in IMPORTANT_MARKDOWN_FILES:
            lines = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8").splitlines()
            self.assertGreater(
                len(lines),
                10,
                f"{relative_path} should have normal Markdown line breaks.",
            )

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
