"""Unit tests for engine.py. Run with:  python -m unittest discover tests -v"""
import os, sys, unittest
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data, engine


class TestImpact(unittest.TestCase):
    def test_price_times_multiplier(self):
        # 100 USD of leather shoes at 0.70 kg/USD = 70 kg
        self.assertEqual(engine.calculate_impact(100, "USD ($)", "Leather shoes"), 70.0)

    def test_second_hand_is_much_lower_than_fast_fashion(self):
        a = engine.calculate_impact(50, "USD ($)", "Fast-fashion clothing")
        b = engine.calculate_impact(50, "USD ($)", "Second-hand clothing")
        self.assertLess(b, a / 3)

    def test_ethical_brand_discount(self):
        plain = engine.calculate_impact(100, "USD ($)", "New furniture")
        ethical = engine.calculate_impact(100, "USD ($)", "New furniture", ethical=True)
        self.assertAlmostEqual(ethical, plain * data.ETHICAL_BRAND_FACTOR, places=2)

    def test_currency_conversion(self):
        self.assertAlmostEqual(engine.to_usd(1000, "INR (\u20b9)"), 12.0)

    def test_zero_or_negative_price(self):
        self.assertEqual(engine.calculate_impact(0, "USD ($)", "Leather shoes"), 0.0)
        self.assertEqual(engine.calculate_impact(-5, "USD ($)", "Leather shoes"), 0.0)

    def test_every_type_has_alternatives_and_valid_swap(self):
        for name, info in data.PRODUCT_TYPES.items():
            self.assertIn(name, data.ALTERNATIVES)
            if info["swap_to"]:
                self.assertLess(data.PRODUCT_TYPES[info["swap_to"]]["multiplier"], info["multiplier"])


class TestPurchases(unittest.TestCase):
    def test_blank_brand_defaults(self):
        p = engine.make_purchase("New books", "   ", 10, "USD ($)", date(2026, 1, 5))
        self.assertEqual(p["brand"], "Unbranded / local")

    def test_ethical_brand_detected_case_insensitive(self):
        p = engine.make_purchase("Recycled-material shoes", "VEJA", 60, "USD ($)", date(2026, 1, 5))
        self.assertTrue(p["ethical"])
        self.assertTrue(p["green"])

    def test_green_choice_rules(self):
        self.assertTrue(engine.is_green_choice("Second-hand books", False))     # eco tier
        self.assertTrue(engine.is_green_choice("Leather shoes", True))          # ethical brand
        self.assertFalse(engine.is_green_choice("Leather shoes", False))

    def test_swap_saving(self):
        swap, saved = engine.swap_saving(100, "USD ($)", "Fast-fashion clothing")
        self.assertEqual(swap, "Second-hand clothing")
        self.assertEqual(saved, 42.0)                      # 50 - 8
        self.assertEqual(engine.swap_saving(100, "USD ($)", "Second-hand clothing"), (None, 0.0))


class TestMonthlyAndBadges(unittest.TestCase):
    def setUp(self):
        self.demo = engine.demo_purchases(date(2026, 6, 15))

    def test_demo_has_15_purchases(self):
        self.assertEqual(len(self.demo), 15)

    def test_month_filter_and_totals(self):
        june = engine.monthly_summary(self.demo, 2026, 6)
        may = engine.monthly_summary(self.demo, 2026, 5)
        self.assertEqual(june["count"] + may["count"], 15)
        self.assertGreater(may["total_co2"], june["total_co2"])   # last month was heavier

    def test_empty_month(self):
        s = engine.monthly_summary(self.demo, 2020, 1)
        self.assertEqual((s["count"], s["total_co2"], s["green_share"]), (0, 0.0, 0))

    def test_traffic_light(self):
        self.assertEqual(engine.footprint_status(30, 60), "green")
        self.assertEqual(engine.footprint_status(50, 60), "amber")
        self.assertEqual(engine.footprint_status(80, 60), "red")

    def test_badges_demo_this_month(self):
        got = engine.evaluate_badges(self.demo, 2026, 6, 60)
        for expected in ("first_step", "tracker", "low_impact", "ethical", "second_life", "green_streak"):
            self.assertIn(expected, got)
        self.assertNotIn("eco_saver", got)      # needs <= 30 kg

    def test_eco_saver_with_bigger_goal(self):
        self.assertIn("eco_saver", engine.evaluate_badges(self.demo, 2026, 6, 100))

    def test_no_badges_for_new_user(self):
        self.assertEqual(engine.evaluate_badges([], 2026, 6, 60), [])

    def test_green_streak_broken_by_non_green(self):
        items = [engine.make_purchase("Second-hand books", "", 5, "USD ($)", date(2026, 6, d)) for d in (1, 2)]
        items.append(engine.make_purchase("Leather shoes", "", 80, "USD ($)", date(2026, 6, 3)))
        self.assertNotIn("green_streak", engine.evaluate_badges(items, 2026, 6, 60))

    def test_new_badges_diff(self):
        self.assertEqual(engine.new_badges(["a"], ["a", "b"]), ["b"])


if __name__ == "__main__":
    unittest.main()
