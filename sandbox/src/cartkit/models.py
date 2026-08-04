"""Domain models for cart pricing."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LineItem:
    """A single line in a cart.

    unit_price_cents may be negative for credit lines (e.g. shipping credits).
    """

    sku: str
    unit_price_cents: int
    quantity: int = 1


@dataclass
class Coupon:
    """A discount.

    kind:
        "percent" -> value is percentage points off (0-100)
        "fixed"   -> value is a flat amount in cents off
    max_discount_cents:
        Optional cap on how much this coupon may ever take off.
        Contractually applies to every coupon kind.
    """

    code: str
    kind: str
    value: int
    max_discount_cents: Optional[int] = None


@dataclass
class Cart:
    items: List[LineItem] = field(default_factory=list)
