from pyfiglet import Figlet
from app.calculator import Calculator

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

    try:
        while True:
            user_input = input(">>> ")
            user_input = user_input.lower()
            if user_input == "exit":
                print("Exiting calculator... Goodbye ~")
                break
            elif user_input == "history":
                history = calculator.get_history()
                if not history:
                    print("No history yet.")
                else:
                    for i, calc in enumerate(history, start=1):
                        print(f"{i}. {calc}")
                continue
            elif user_input == "save":
                calculator.save_history()
                print("History saved to disk.")
                continue
            elif user_input == "clear":
                calculator.clear_history()
                print("History has been cleared.")
                continue
            
            try:
                operation, a, b = user_input.split()
                a, b = float(a), float(b)
                result = calculator.calculate(operation, a, b).result
                print(f"Result: {result}")
            except ValueError as e:
                print(f"Error: {e}")
                continue
            except ZeroDivisionError as e:
                print(f"Error: {e}")
                continue

    finally:
        calculator.shutdown()
        