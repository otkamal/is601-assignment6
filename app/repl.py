from pyfiglet import Figlet
from app.calculator import Calculator
from app.calculation import CalculationFactory

def start_repl(calculator: Calculator) -> None:
    """
    Runs an interactive calculator REPL (Read-Eval-Print Loop).

    Prompts the user to enter an operation and two numbers in the format
    <operation> <a> <b>, computes the result, and prints it. Continues
    until the user types 'exit'.

    Supported operations:
        - add: Adds a and b.
        - subtract: Subtracts b from a.
        - multiply: Multiplies a and b.
        - divide: Divides a by b.

    Raises:
        ZeroDivisionError: If divide is used and b is zero (handled internally).
        ValueError: If the input format is invalid (handled internally).

    Example:
        >>> calculator()
        Enter an operation and two numbers, or 'exit' to quit: add 5 3
        Result: 8.0
    """

    startscreen = Figlet(font="slant")
    print(startscreen.renderText("Calculator REPL"))
    print("Type 'exit' to quit.")
    print("Enter an operation and two numbers, or 'exit' to quit.")
    print("Enter 'help' to see available operations or 'history' to see previously ran operations.")

    #history: list[tuple[Calculation, float]] = []
    while True:
        user_input = input(">>> ")
        user_input = user_input.lower()
        if user_input == "exit":
            print("Exiting calculator... Goodbye ~")
            break
        # elif user_input == "help":
        #     dummy_factory = CalculationFactory()
        #     operations = ", ".join(dummy_factory.get_supported_operations())
        #     print(f"Supported operations: {operations}, history, help, and exit.")
        #     continue
        # elif user_input == "history":
        #     for calc, result in history:
        #         print(f"- {str(calc)} = {result}")
        #     continue

        try:
            operation, a, b = user_input.split()
            a, b = float(a), float(b)
        except ValueError:
            print("Invalid input. Please follow <operation> <a> <b> syntax.")
            continue

        calculation = CalculationFactory.build_calculation(operation, a, b)
        result = calculator.calculate(calculation)
        print(result)
        
        # try:
        #     #calculation = CalculationFactory.build_calculation(operation, a, b)
        #     #result = calculation.execute()
        #     #history.append((calculation, result))
        #     print(f"Result: {result}")
        # except ValueError as err:
        #     print(err)
        #     continue
        # except ZeroDivisionError as err:
        #     print(err)
        #     continue
