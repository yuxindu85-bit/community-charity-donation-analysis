import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.analyze_charity_sale import load_data, make_summaries


class CharitySaleAnalysisTest(unittest.TestCase):
      def setUp(self) -> None:
                self.donations, self.sales = load_data()

      def test_direct_donation_total(self) -> None:
                self.assertEqual(self.donations["amount_cny"].sum(), 26870)

      def test_sale_revenue_total(self) -> None:
                self.assertEqual(self.sales["revenue_cny"].sum(), 1751)

      def test_sale_net_contribution_is_positive(self) -> None:
                self.assertTrue((self.sales["net_contribution_cny"] > 0).all())

      def test_team_summary_covers_all_sources(self) -> None:
                _, _, team_summary, _ = make_summaries(self.donations, self.sales)
                total = team_summary["total_contribution_cny"].sum()
                expected = self.donations["amount_cny"].sum() + self.sales["net_contribution_cny"].sum()
                self.assertEqual(total, expected)


if __name__ == "__main__":
      unittest.main()
  
