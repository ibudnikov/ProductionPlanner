class Character:
    brokerRelations = 0
    accounting = 0

    def getBrokerCharge(self):
        return 0.03-0.001*self.brokerRelations

    def getTax(self):
        return 0.02*(1-0.1*self.accounting)

def init():
    c = Character()
    return c
