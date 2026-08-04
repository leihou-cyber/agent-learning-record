"""购物车计价的领域模型。"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LineItem:
    """购物车中的一行商品。

    unit_price_cents 允许为负数，用于表示抵扣行（例如运费补贴）。
    """

    sku: str
    unit_price_cents: int
    quantity: int = 1


@dataclass
class Coupon:
    """优惠券。

    kind:
        "percent" -> value 表示折扣百分点（0-100）
        "fixed"   -> value 表示直接减免的金额（分）
    max_discount_cents:
        该券最多能优惠的金额上限（分）。
        按契约，这个上限对**所有**券种都生效。
    """

    code: str
    kind: str
    value: int
    max_discount_cents: Optional[int] = None


@dataclass
class Cart:
    items: List[LineItem] = field(default_factory=list)
