"""Existing regression suite. These all pass today and must keep passing."""
import pytest

from cartkit import Cart, Coupon, LineItem, apply_coupon, subtotal_cents, total_cents


def cart(*pairs):
    return Cart(items=[LineItem(sku=s, unit_price_cents=p, quantity=q) for s, p, q in pairs])


class TestSubtotal:
    def test_empty_cart_is_zero(self):
        assert subtotal_cents(Cart()) == 0

    def test_single_item(self):
        assert subtotal_cents(cart(("A", 1000, 1))) == 1000

    def test_quantity_multiplies(self):
        assert subtotal_cents(cart(("A", 1000, 3))) == 3000

    def test_multiple_items(self):
        assert subtotal_cents(cart(("A", 1000, 2), ("B", 250, 4))) == 3000

    def test_negative_credit_line(self):
        assert subtotal_cents(cart(("A", 1000, 1), ("SHIP-CREDIT", -300, 1))) == 700


class TestPercentCoupon:
    def test_ten_percent(self):
        assert apply_coupon(1000, Coupon("C", "percent", 10)) == 900

    def test_hundred_percent(self):
        assert apply_coupon(1000, Coupon("C", "percent", 100)) == 0

    def test_zero_percent(self):
        assert apply_coupon(1000, Coupon("C", "percent", 0)) == 1000

    def test_rounds_half_up(self):
        # 5% of 1005 = 50.25 -> 50
        assert apply_coupon(1005, Coupon("C", "percent", 5)) == 955
        # 50% of 101 = 50.5 -> 51
        assert apply_coupon(101, Coupon("C", "percent", 50)) == 50

    def test_percent_respects_cap(self):
        # 50% of 10000 = 5000, capped at 1500
        assert apply_coupon(10000, Coupon("C", "percent", 50, max_discount_cents=1500)) == 8500


class TestFixedCoupon:
    def test_flat_discount(self):
        assert apply_coupon(1000, Coupon("C", "fixed", 250)) == 750

    def test_never_below_zero(self):
        assert apply_coupon(1000, Coupon("C", "fixed", 5000)) == 0


class TestUnknownKind:
    def test_raises(self):
        with pytest.raises(ValueError):
            apply_coupon(1000, Coupon("C", "bogus", 1))


class TestTotal:
    def test_no_coupons(self):
        assert total_cents(cart(("A", 1000, 2)), []) == 2000

    def test_coupons_applied_in_sequence(self):
        # 2000 -> -10% -> 1800 -> -300 -> 1500
        coupons = [Coupon("P", "percent", 10), Coupon("F", "fixed", 300)]
        assert total_cents(cart(("A", 1000, 2)), coupons) == 1500

    def test_order_matters(self):
        forward = total_cents(cart(("A", 1000, 1)), [Coupon("F", "fixed", 500), Coupon("P", "percent", 50)])
        backward = total_cents(cart(("A", 1000, 1)), [Coupon("P", "percent", 50), Coupon("F", "fixed", 500)])
        assert forward == 250
        assert backward == 0
