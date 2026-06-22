import datetime

class CalculatorMemento():

    def __init__(self, calculator):
        self._timestamp = datetime.datetime.now()
        self._history = calculator.get_history()

    def get_history(self):
        return list(self._history)
    
    def get_timestamp(self):
        return self._timestamp
