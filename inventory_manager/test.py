from pprint import pprint
from .inventory.inv import Bin

a = Bin("inv_id", "Box")
pprint(a.parts)
