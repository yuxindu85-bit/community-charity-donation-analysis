import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from llm_review import (
    build_review_prompt,
    generate_llm_review,
    generate_offline_review,
    load_event_context,
)


class LlmReviewTest(unittest.TestCase):
    def test_event_context_uses_existing_summary_data(self):
        context = load_event_context()

        self.assertGreater(context["total_direct_donations"], 0)
        self.assertGreater(context["total_sale_revenue"], 0)
        self.assertGreater(context["total_funds"], 26000)
        self.assertNotEqual(context["top_sale_category"], "Not available")
        self.assertNotEqual(context["top_booth"], "Not available")

    def test_prompt_keeps_project_positioning_honest(self):
        context = load_event_context()
        prompt = build_review_prompt(context)

        self.assertIn("anonymized", prompt)
        self.assertIn("not an official financial report", prompt)
        self.assertIn("exploratory", prompt)
        self.assertIn("Total funds raised", prompt)
        self.assertNotIn("AI-powered", prompt)
        self.assertNotIn("official audit", prompt)

    def test_offline_review_can_be_generated_without_api_keys(self):
        context = load_event_context()
        review_text = generate_offline_review(context)

        self.assertIn("offline mode", review_text)
        self.assertIn("not use GPT or DeepSeek", review_text)
        self.assertIn("official financial report", review_text)
        self.assertIn("Possible next improvements", review_text)

    def test_offline_review_writes_markdown_file(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "llm_review.md"
            written_path = generate_llm_review(
                provider="offline",
                output_path=output_path,
            )

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertGreater(len(output_path.read_text(encoding="utf-8")), 200)


if __name__ == "__main__":
    unittest.main()
