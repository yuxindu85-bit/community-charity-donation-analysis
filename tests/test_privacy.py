import re
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_COLUMNS = {
    "real_name",
    "phone_number",
    "email",
    "address",
    "school_name",
    "contact",
    "wechat_id",
    "payment_account",
    "qr_code",
}

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"\b1[3-9]\d{9}\b")


class PrivacyTest(unittest.TestCase):
    def test_csv_files_do_not_include_private_columns(self):
        csv_files = list((PROJECT_ROOT / "data").rglob("*.csv"))
        csv_files += list((PROJECT_ROOT / "reports" / "summary_tables").rglob("*.csv"))

        for file_path in csv_files:
            dataframe = pd.read_csv(file_path)
            self.assertFalse(
                PRIVATE_COLUMNS.intersection(set(dataframe.columns)),
                f"Private column found in {file_path}",
            )

    def test_csv_files_do_not_include_obvious_contact_values(self):
        for file_path in (PROJECT_ROOT / "data").rglob("*.csv"):
            text = file_path.read_text(encoding="utf-8")
            self.assertIsNone(EMAIL_PATTERN.search(text), f"Email found in {file_path}")
            self.assertIsNone(PHONE_PATTERN.search(text), f"Phone number found in {file_path}")

    def test_event_image_filenames_are_marked_blurred(self):
        image_dir = PROJECT_ROOT / "docs" / "images"
        if not image_dir.exists():
            return

        image_files = [
            path
            for path in image_dir.iterdir()
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        for image_path in image_files:
            if image_path.name == "dashboard_overview.png":
                continue
            self.assertIn("blurred", image_path.name)


if __name__ == "__main__":
    unittest.main()
