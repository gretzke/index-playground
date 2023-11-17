from simulation import Simulation


class Token():
    symbol: str
    amount: float
    weight: float

    def __init__(self, symbol: str, amount: float, weight: float = None):
        self.symbol = symbol
        self.amount = amount
        self.weight = amount
        if (weight != None):
            self.weight = weight


class Index(Simulation):

    tokens: list[Token]

    def __init__(self, tokens: list[Token], daysToSimulate: int = 0):
        super().__init__()
        if (daysToSimulate > 0):
            self.randomise(days=daysToSimulate)

        self.tokens = tokens
