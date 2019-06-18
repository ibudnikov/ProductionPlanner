class System:
    manufacturingIndex = 0
    timeIndex = 0
    materialIndex = 0
    copyIndex = 0
    inventionIndex = 0
    reversingIndex = 0
    reactionIndex = 0
    
    customsTax = 0.05

    def __init__(self, name):
        self.manufacturingIndex = 0.01
        self.timeIndex = 0.01
        self.materialIndex = 0.01
        self.copyIndex = 0.01
        self.inventionIndex = 0.01
        self.reversingIndex = 0.01
        self.reactionIndex = 0.01

def init():
    s = System('TestSystem')
    return s
