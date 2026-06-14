from abc import ABC, abstractmethod
from app.operations import Operations

class Calculation(ABC):
    def __init__(self, a: float, b: float):
        self.operand_a = a
        self.operand_b = b
        
    @abstractmethod
    def execute(self) -> float:
        pass

class CalculationFactory:
    _calculations = {}
    
    @classmethod
    def register_calculation(cls, calc: str):
        def registration_decorator(subclass):
            cls._calculations[calc] = subclass
            return subclass
        return registration_decorator
    
    @classmethod
    def build_calculation(cls, calc: str, a: float, b: float) -> Calculation:
        new_calculation = cls._calculations.get(calc)
        return new_calculation(a, b)
    
@CalculationFactory.register_calculation('add')
class Addition(Calculation):
    def execute(self) -> float:
        return Operations.addition(self.operand_a, self.operand_b)
    
@CalculationFactory.register_calculation('subtract')
class Subtraction(Calculation):
    def execute(self) -> float:
        return Operations.subtraction(self.operand_a, self.operand_b)

@CalculationFactory.register_calculation('multiply') 
class Multiplication(Calculation):
    def execute(self) -> float:
        return Operations.multiplication(self.operand_a, self.operand_b)

@CalculationFactory.register_calculation('divide') 
class Division(Calculation):
    def execute(self) -> float:
        return Operations.division(self.operand_a, self.operand_b)