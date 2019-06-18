class Facility:
    tax = 0
    standing = 0
    def __init__(self, tax, standings):
        self.tax = tax
        self.standings = standings

def init():
    f = Facility(0.03, 0)
    return f
