from dataclasses import dataclass
from decimal import setcontext, Context, MAX_PREC, MAX_EMAX, MIN_EMIN, Decimal
from datetime import date
from functools import reduce

setcontext(Context(prec=MAX_PREC, Emax=MAX_EMAX, Emin=MIN_EMIN))


@dataclass
class Order:
    @dataclass
    class OrderItem:
        unit_price: Decimal
        qty: int
        description: str
        uuid: str

        def total_price(self) -> Decimal:
            return self.unit_price * self.qty

    id: str
    pdf_url: str
    bill_name: str
    misc_fees: Decimal  # taxes, delivery, etc
    items: list[OrderItem]
    order_date: date
    expected_arrival: date
    vendor: str
    has_arrived: bool

    def total_price(self) -> Decimal:
        return self.misc_fees + reduce(
            lambda x, i: x + i.total_price(), self.items, Decimal(0)
        )
