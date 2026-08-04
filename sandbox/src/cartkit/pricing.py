"""Cart pricing.

Contract (this is the spec; the code is expected to honour it):

1. subtotal_cents(cart)
   Sum of unit_price_cents * quantity over all items.

2. apply_coupon(subtotal, coupon)
   - "percent": take value% off, rounded to the nearest cent, half-up.
   - "fixed":   take `value` cents off.
   - The result is never below zero.
   - If coupon.max_discount_cents is set, the discount actually taken
     must never exceed it, for EVERY coupon kind.

3. total_cents(cart, coupons)
   Coupons are applied in order, each to the running total.
"""
from typing import List

from .models import Cart, Coupon


def subtotal_cents(cart: Cart) -> int:
    total = 0
    for item in cart.items:
        total += item.unit_price_cents * item.quantity
    return total


def _round_half_up(value: float) -> int:
    """Round to the nearest integer, .5 always going away from zero."""
    if value < 0:
        return -int(-value + 0.5)
    return int(value + 0.5)


def apply_coupon(subtotal_cents_value: int, coupon: Coupon) -> int:
    """Return the new total after applying one coupon."""
    if coupon.kind == "percent":
        discount = _round_half_up(subtotal_cents_value * coupon.value / 100)
        if coupon.max_discount_cents is not None:
            discount = min(discount, coupon.max_discount_cents)
    elif coupon.kind == "fixed":
        discount = coupon.value
    else:
        raise ValueError("unknown coupon kind: {}".format(coupon.kind))

    result = subtotal_cents_value - discount
    if result < 0:
        return 0
    return result


def total_cents(cart: Cart, coupons: List[Coupon]) -> int:
    running = subtotal_cents(cart)
    for coupon in coupons:
        running = apply_coupon(running, coupon)
    return running
