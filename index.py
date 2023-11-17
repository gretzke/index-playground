import math

from lib.util import get_traceback
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
    # index token supply
    supply: float = 0.0
    # the sum of the weight of all tokens
    totalWeight: float = 0.0
    # the amount of index tokens equivalent to a single token of a backing asset
    indexTokenPerToken: list[float]

    def __init__(self, tokens: list[Token], daysToSimulate: int = 0):
        super().__init__()
        if (daysToSimulate > 0):
            self.randomise(days=daysToSimulate)

        self.tokens = tokens

        totalSupply = 1.0
        for token in tokens:
            totalSupply = math.sqrt(
                1 if token.amount == 0 else token.amount * totalSupply)
            self.totalWeight += token.weight

        self.supply = 1000  # totalSupply

        # these values are basically how many index tokens should the protocol mint for a given asset if the minting boding curve was linear to have an equal value
        self.indexTokenPerToken = []
        for token in tokens:
            self.indexTokenPerToken.append(
                self.priceOf(token.symbol) * self.supply / self.totalValueOf())

    def failsafe(f):
        def decorator(self, index, *args, simulate=False, **kwargs):
            snapshot = self.createSnapshot(index)
            result = None
            try:
                result = f(self, index, *args, **kwargs)
                if simulate:
                    self.restoreSnapshot(snapshot)
            except Exception as e:
                print(get_traceback(e))
                self.restoreSnapshot(snapshot)
                raise e
            return result
        return decorator

    @failsafe
    def mintUsd(self, index, usd) -> float:
        amount = usd / self.priceOf(self.tokens[index].symbol)
        return self.__mint(index, amount) * self.price()

    @failsafe
    def mint(self, index, amount) -> float:
        return self.__mint(index, amount)

    def mintAmountOut(self, index, amountIn) -> float:
        targetSupply = self.targetIndexPerBacking(index)
        if (self.tokens[index].amount > targetSupply):
            # token balance exceeds target amount based on weights
            print("token balance exceeds target amount based on weights")
            return 0

        newSupply = self.__indexPerBacking(
            index, self.tokens[index].amount + amountIn)
        amountOut = newSupply - self.currentIndexPerBacking(index)
        if (amountOut < 0):
            print("newSupply < self.supply")
            return 0

        return amountOut

    def targetIndexPerBacking(self, index) -> float:
        """
        @notice The target amount of index allocated to a backing asset based on their weight internally
        """
        return self.supply * self.indexTokenPerToken[index] * self.tokens[index].weight * 100 / self.totalWeight

    def currentIndexPerBacking(self, index) -> float:
        return self.__indexPerBacking(index, self.tokens[index].amount)

    def totalValueOf(self) -> float:
        totalValue = 0
        for token in self.tokens:
            totalValue += token.amount * self.priceOf(token.symbol)
        return totalValue

    def price(self):
        return self.totalValueOf() / self.supply

    def log(self):
        print(f"Index supply: {self.supply}")
        totalValue = self.totalValueOf()
        for i, token in enumerate(self.tokens):
            print(
                f"{round(token.amount, 4)} {token.symbol}: Value ${round(self.priceOf(token.symbol) * token.amount, 2)}, Price: ${round(self.priceOf(token.symbol), 2)} ({round(self.priceOf(token.symbol) * token.amount / totalValue * 100, 2)}%), Index backing: {self.targetIndexPerBacking(i)}")
        print(f"Average value: ${round(totalValue / len(self.tokens), 2)}")
        print(
            f"Index value: ${round(totalValue, 2)}, index price: ${round(totalValue / self.supply, 5)}")
        print()
        return self

    def __mint(self, index: int, amountIn: float) -> float:
        amountOut = self.mintAmountOut(index, amountIn)

        self.tokens[index].amount += amountIn
        self.supply += amountOut
        return amountOut

    def __indexPerBacking(self, index, amount) -> float:
        """
        this formula is a function of the index token supply for a particular backing asset based on the amount of tokens in the pool. For 0 index tokens the supply should be 0. The functions converges towards `targetSupply`. The `indexTokenPerToken` is the tangent of the function at the (0,0) point. This ensures that the tokens are minted initially at the correct ratio, should the index token be initialized without and of these tokens.
        """
        targetSupply = self.targetIndexPerBacking(index)
        return targetSupply * \
            (1 - 1 /
             (self.indexTokenPerToken[index]*amount/(targetSupply) + 1))

    def createSnapshot(self, index):
        return {
            "token": {
                "index": index,
                "amount": self.tokens[index].amount
            },
            "supply": self.supply,
        }

    def restoreSnapshot(self, snapshot):
        self.tokens[snapshot["token"]["index"]
                    ].amount = snapshot["token"]["amount"]
        self.supply = snapshot["supply"]
