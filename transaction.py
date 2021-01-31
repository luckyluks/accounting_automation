from dateutil import parser
from enum import Enum


class TransactionType(Enum):
    EXPENSE = 0
    INTAKE = 1

class BookingPurpose(Enum):
    Abschluss = 0
    Dauerauftrag = 1
    Gutschrift = 2
    Kartenabrechnungg = 3
    Lastschrift = 4
    Gehalt = 5
    Ueberweisung = 6

class Transaction():
    def __init__(self, item):
        self.value          = item["Betrag"]
        self.type           = item["Buchungstext"]
        # self.date_booking   = parser.parse(item["Buchungstag"])
        self.date_value     = parser.parse(item["Wertstellung"])
        self.purpose        = item["Verwendungszweck"]
        self.initiator      = item["Auftraggeber"]
