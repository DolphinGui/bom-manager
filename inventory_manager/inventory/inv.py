from dataclasses import dataclass
from enum import Enum
from .order import Order
from uuid import UUID
from ..backend.base import AccessKey, Table
from ..cache import global_config
from ..backend.factories import get_key

schema = [
    "Type",
    "Value",
    "Package",
    "Qty",
    "LCSC ID",
    "Digikey ID",
    "Mouser ID",
    "Purchase URL",
    "Description",
    "Device Marking",
    "Comments",
    "Aliases",
    "UUID",
]


def fuzzy_convert(num: str) -> str | float:
    if num.isnumeric():
        return float(num)
    return num


@dataclass(init=False)
class Part:
    class Type(Enum):
        resistor = "Resistor"
        capacitor = "Capacitor"
        inductor = "Inductor"
        Fuse = "Fuse"
        diode = "Diode"
        ic = "IC"
        component = "Component"
        connector = "Connector"

    type: Type
    value: str | float
    package: str
    qty: int
    lcsc_id: str
    digikey_id: str
    mouser_id: str
    purchase_url: str
    description: str
    marking: str
    comments: str
    aliases: str
    uuid: UUID

    def to_str_list(self) -> list[str]:
        return [
            self.type.value,
            str(self.value),
            self.package,
            str(self.qty),
            self.lcsc_id,
            self.digikey_id,
            self.mouser_id,
            self.purchase_url,
            self.description,
            self.marking,
            self.comments,
            self.aliases,
            str(self.uuid),
        ]

    # def create(self, **kwargs):
    #     self.type = Part.Type(kwargs["Type"])
    #     self.value = fuzzy_convert(kwargs["Value"])
    #     self.package = kwargs["Package"]
    #     self.qty = kwargs["Quantity"]
    #     self.lcsc_id = kwargs["LCSC ID"]
    #     self.digikey_id = kwargs["Digikey ID"]
    #     self.mouser_id = kwargs["Mouser ID"]
    #     self.description = kwargs["Description"]
    #     self.marking = kwargs["Marking"]
    #     self.comments = kwargs["Comments"]
    #     self.aliases = kwargs["Aliases"]
    #     self.UUID = kwargs["UUID"]

    def __init__(self, *args):
        self.type = Part.Type(args[0])
        self.value = fuzzy_convert(args[1])
        self.package = args[2]
        self.qty = args[3]
        self.lcsc_id = args[4]
        self.digikey_id = args[5]
        self.mouser_id = args[6]
        self.purchase_url = args[7]
        self.description = args[8]
        self.marking = args[9]
        self.comments = args[10]
        self.aliases = args[11]
        self.uuid = UUID(args[12])


class Bin:
    parts: list[tuple[Part, bool]]
    orders: list[tuple[Order, bool]]
    table: Table
    sheet: str

    def __init__(self, table_type: str, sheet: str):
        key = get_key()
        self.table = key.get_table(global_config[table_type])
        self.sheet = sheet
        data = self.table.get_data(sheet)
        if data[0] != schema:
            raise RuntimeError("Schema does not match!")
        self.parts = [(Part(*x), bool(False)) for x in data[1:]]

    # def get_str(self)->list[list[str]]:
    # return [[]]
