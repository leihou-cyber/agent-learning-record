"""购物车计价逻辑。

契约（这是规格说明，代码应当遵守它）：

1. subtotal_cents(cart)
   对所有商品行求和：unit_price_cents * quantity。

2. apply_coupon(subtotal, coupon)
   - "percent"：按 value% 优惠，四舍五入到分（.5 向上进位）。
   - "fixed"：直接减免 value 分。
   - 结果永不小于 0。
   - 若设置了 coupon.max_discount_cents，则实际优惠金额不得超过该上限，
     此规则对**所有**券种生效。

3. total_cents(cart, coupons)
   多张券按顺序依次作用于当前余额。
"""
from typing import List

from .models import Cart, Coupon


def subtotal_cents(cart: Cart) -> int:
    total = 0
    for item in cart.items:
        total += item.unit_price_cents * item.quantity
    return total


def _round_half_up(value: float) -> int:
    """四舍五入到最近整数，.5 一律远离零方向进位。"""
    if value < 0:
        return -int(-value + 0.5)
    return int(value + 0.5)


def apply_coupon(subtotal_cents_value: int, coupon: Coupon) -> int:
    """应用一张券，返回优惠后的新余额。"""
    if coupon.kind == "percent":
        discount = _round_half_up(subtotal_cents_value * coupon.value / 100)
        if coupon.max_discount_cents is not None:
            discount = min(discount, coupon.max_discount_cents)
    elif coupon.kind == "fixed":
        discount = coupon.value
    else:
        raise ValueError("未知的券种：{}".format(coupon.kind))

    result = subtotal_cents_value - discount
    if result < 0:
        return 0
    return result


def total_cents(cart: Cart, coupons: List[Coupon]) -> int:
    running = subtotal_cents(cart)
    for coupon in coupons:
        running = apply_coupon(running, coupon)
    return running
