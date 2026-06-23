import datetime

class CalculatorMemento():
    """Snapshot of a Calculator's history at a point in time.

    Used by Calculator to support undo and redo. Captures history and
    timestamp at construction; neither changes after that.
    """

    def __init__(self, calculator):
        """Capture the calculator's current history and record the timestamp.

        Args:
            calculator: The Calculator instance to snapshot.
        """
        self._timestamp = datetime.datetime.now()
        self._history = calculator.get_history()

    def get_history(self):
        """Return a copy of the snapshotted history list.

        Returns:
            A new list of Calculation objects from the time of the snapshot.
        """
        return list(self._history)

    def get_timestamp(self):
        """Return the datetime when this snapshot was taken.

        Returns:
            A datetime.datetime instance.
        """
        return self._timestamp
