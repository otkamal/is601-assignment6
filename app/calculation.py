from abc import ABC, abstractmethod
from app.operations import Operations
from typing import Optional


class Calculation(ABC):

    """
    Abstract base class representing a calculation with two operands.

    All subclasses must implement the execute method, which performs
    the calculation and returns a float result.

    Methods:
        execute(): Performs the calculation and returns the result.
    """

    def __init__(self, a: float, b: float, result: Optional[float] = None):
        """Initialize the calculation with two operands and an optional result.

        Args:
            a: The first operand.
            b: The second operand.
            result: Pre-computed result, or None if execute() has not been called yet.
        """
        self.operand_a = a
        self.operand_b = b
        self.result = result

    @abstractmethod
    def execute(self) -> float:
        """
        Executes the calculation and returns the result.

        Returns:
            The result of the calculation as a float.
        """

    def __str__(self) -> str:
        """Return a human-readable string representation of the calculation.

        Returns:
            A string in the format 'ClassName(a = <a>, b = <b>, result = <result>)'.
        """
        return f"{self.__class__.__name__}(a = {self.operand_a}, b = {self.operand_b}, result = {self.result})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the calculation for debugging.

        Returns:
            A string in the format 'ClassName: operand_a = <a>, operand_b = <b>, result = <result>'.
        """
        return f"{self.__class__.__name__}: operand_a = {self.operand_a}, operand_b = {self.operand_b}, result = {self.result}"

    def to_dict(self) -> dict:
        """Serialize this calculation to a dictionary.

        Returns:
            A dict with keys 'operation', 'operand_a', 'operand_b', and 'result'.
        """
        operation = next(k for k, v in CalculationFactory._calculations.items() if v == self.__class__)
        return {
            "operation": operation,
            "operand_a": self.operand_a,
            "operand_b": self.operand_b,
            "result": self.result
        }


class CalculationFactory:

    """
    Factory for registering and instantiating Calculation subclasses.

    Subclasses are registered via the register_calculation decorator and
    retrieved by name through build_calculation.

    Methods:
        register_calculation(calc): Decorator to register a Calculation subclass.
        build_calculation(calc, a, b): Instantiates a registered Calculation by name.
    """

    _calculations = {}

    @classmethod
    def register_calculation(cls, calc: str):
        """
        Decorator that registers a Calculation subclass under the given name.

        Args:
            calc: The operation name to register (case-insensitive).

        Returns:
            A decorator that registers the decorated class and returns it unchanged.

        Raises:
            ValueError: If the operation name is already registered.
        """
        def registration_decorator(subclass):
            calc_sanitized = calc.lower()
            if calc_sanitized in cls._calculations:
                raise ValueError(f"{calc_sanitized} is already registered.")
            cls._calculations[calc_sanitized] = subclass
            return subclass
        return registration_decorator

    @classmethod
    def build_calculation(cls, calc: str, a: float, b: float) -> Calculation:
        """
        Instantiates a registered Calculation by name.

        Args:
            calc: The operation name (case-insensitive).
            a: The first operand.
            b: The second operand.

        Returns:
            A Calculation instance ready to be executed.

        Raises:
            ValueError: If the operation name is not registered.
        """
        calc_sanitized = calc.lower()
        if calc_sanitized not in cls._calculations:
            raise ValueError(f'"{calc_sanitized}" is not a supported operation.')
        new_calculation = cls._calculations.get(calc_sanitized)
        return new_calculation(a, b)

    @classmethod
    def get_supported_operations(cls):
        """
        Returns the names of all registered operations.

        Returns:
            A view of the registered operation name strings.
        """
        return cls._calculations.keys()

    @classmethod
    def from_dict(cls, data: dict) -> Calculation:
        """Deserialize a Calculation from a dictionary.

        Args:
            data: A dict with keys 'operation', 'operand_a', 'operand_b', and 'result'.

        Returns:
            A Calculation instance with result already set.

        Raises:
            ValueError: If the operation name is not registered.
        """
        calc = cls.build_calculation(
            data["operation"],
            float(data["operand_a"]),
            float(data["operand_b"])
        )
        calc.result = float(data["result"])
        return calc


@CalculationFactory.register_calculation('add')
class Addition(Calculation):

    """
    Calculation that adds two operands.

    Methods:
        execute(): Returns the sum of operand_a and operand_b.
    """

    def execute(self) -> float:
        """
        Adds the two operands.

        Returns:
            The sum of operand_a and operand_b.
        """
        self.result = Operations.addition(self.operand_a, self.operand_b)
        return self.result


@CalculationFactory.register_calculation('subtract')
class Subtraction(Calculation):

    """
    Calculation that subtracts the second operand from the first.

    Methods:
        execute(): Returns the difference of operand_a and operand_b.
    """

    def execute(self) -> float:
        """
        Subtracts operand_b from operand_a.

        Returns:
            The difference of operand_a and operand_b.
        """
        self.result = Operations.subtraction(self.operand_a, self.operand_b)
        return self.result


@CalculationFactory.register_calculation('multiply')
class Multiplication(Calculation):

    """
    Calculation that multiplies two operands.

    Methods:
        execute(): Returns the product of operand_a and operand_b.
    """

    def execute(self) -> float:
        """
        Multiplies the two operands.

        Returns:
            The product of operand_a and operand_b.
        """
        self.result = Operations.multiplication(self.operand_a, self.operand_b)
        return self.result


@CalculationFactory.register_calculation('divide')
class Division(Calculation):

    """
    Calculation that divides the first operand by the second.

    Methods:
        execute(): Returns the quotient of operand_a and operand_b.
    """

    def execute(self) -> float:
        """
        Divides operand_a by operand_b.

        Returns:
            The quotient of operand_a and operand_b.

        Raises:
            ZeroDivisionError: If operand_b is zero.
        """
        self.result = Operations.division(self.operand_a, self.operand_b)
        return self.result


@CalculationFactory.register_calculation('power')
class Power(Calculation):

    """
    Calculation that raises the first operand to the power of the second.

    Methods:
        execute(): Returns operand_a raised to the power of operand_b.
    """

    def execute(self) -> float:
        """
        Raises operand_a to the power of operand_b.

        Returns:
            The result of operand_a raised to the power of operand_b.
        """
        self.result = Operations.power(self.operand_a, self.operand_b)
        return self.result


@CalculationFactory.register_calculation('modulus')
class Modulus(Calculation):

    """
    Calculation that returns the remainder of dividing the first operand by the second.

    Methods:
        execute(): Returns the remainder of operand_a divided by operand_b.
    """

    def execute(self) -> float:
        """
        Returns the remainder of dividing operand_a by operand_b.

        Returns:
            The remainder of operand_a divided by operand_b.

        Raises:
            ZeroDivisionError: If operand_b is zero.
        """
        self.result = Operations.modulus(self.operand_a, self.operand_b)
        return self.result

@CalculationFactory.register_calculation('percent')
class Percent(Calculation):

    """
    Calculation that expresses the first operand as a percentage of the second.

    Methods:
        execute(): Returns (operand_a / operand_b) * 100.
    """

    def execute(self) -> float:
        """
        Expresses operand_a as a percentage of operand_b.

        Returns:
            (operand_a / operand_b) * 100.

        Raises:
            ZeroDivisionError: If operand_b is zero.
        """
        self.result = Operations.percent(self.operand_a, self.operand_b)
        return self.result

@CalculationFactory.register_calculation('abs')
class AbsoluteDifference(Calculation):

    """
    Calculation that returns the non-negative difference between two operands.

    Methods:
        execute(): Returns the absolute value of operand_a - operand_b.
    """

    def execute(self) -> float:
        """
        Computes the absolute difference between the two operands.

        Returns:
            The absolute value of operand_a - operand_b.
        """
        self.result = Operations.absolute_difference(self.operand_a, self.operand_b)
        return self.result

@CalculationFactory.register_calculation('int_div')
class IntegerDivision(Calculation):

    """
    Calculation that divides the first operand by the second and truncates to an integer.

    Methods:
        execute(): Returns the floored quotient of operand_a and operand_b.
    """

    def execute(self) -> float:
        """
        Divides operand_a by operand_b and truncates to an integer quotient.

        Returns:
            The floored quotient of operand_a and operand_b.

        Raises:
            ZeroDivisionError: If operand_b is zero.
        """
        self.result = Operations.integer_division(self.operand_a, self.operand_b)
        return self.result

@CalculationFactory.register_calculation('root')
class Root(Calculation):

    """
    Calculation that returns the nth root of the first operand.

    Methods:
        execute(): Returns operand_a raised to the power of 1 / operand_b.
    """

    def execute(self) -> float:
        """
        Computes the operand_b-th root of operand_a.

        Returns:
            operand_a raised to the power of 1 / operand_b.

        Raises:
            ZeroDivisionError: If operand_b is zero.
        """
        self.result = Operations.nth_root(self.operand_a, self.operand_b)
        return self.result