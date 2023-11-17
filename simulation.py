import os
import csv
from random import random


class Simulation():
    __marketData: dict[str, list[float]]
    timestamps: list[int]

    startIndex: int = 0
    timespan: int = 0
    i: int = 0

    underlyingHistory: list[float]

    def __init__(self) -> None:
        self.__marketData = {}
        self.timestamps = []
        self.underlyingHistory = []

        path = "market_data"
        dir_list = os.listdir(path)
        dir_list.remove(".DS_Store")

        with open(os.path.join(path, dir_list[0])) as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header
            for row in reversed(list(reader)):
                self.timestamps.append(int(row[0]))

        self.timespan = len(self.timestamps)
        self.startIndex = 0
        self.i = self.startIndex

        for file in dir_list:
            with open(os.path.join(path, file)) as csvfile:
                name = file.replace(".csv", "")
                self.__marketData[name] = []
                reader = csv.reader(csvfile)
                next(reader)  # skip header
                for row in reversed(list(reader)):
                    self.__marketData[name].append(float(row[6]))

    def randomise(self, days: int = 30):
        if (days > len(self.timestamps) // 24):
            days = (len(self.timestamps) // 24)
        rand = random()
        self.timespan = days * 24
        self.startIndex = int(
            rand * (len(self.timestamps) - self.timespan + 1))
        self.i = self.startIndex
        print(rand, self.startIndex, self.timespan)

    def initialPrice(self, token: str) -> float:
        return self.__marketData[token][self.startIndex]

    def priceOf(self, token: str) -> float:
        return self.__marketData[token][self.i]

    def changePrice(self, token: str, multiplier: float):
        self.__marketData[token][self.i] *= multiplier

    def marketData(self) -> dict[str, list[float]]:
        return (lambda: {key: value[self.startIndex:self.startIndex+self.timespan] for key, value in self.__marketData.items()})()

    def next(self) -> bool:
        if (self.i + 1 >= self.startIndex + self.timespan):
            return False
        self.i += 1
        return True
