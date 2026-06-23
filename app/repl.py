from pyfiglet import Figlet
from app.calculator import Calculator

def start_repl(calculator: Calculator) -> None:
    """Run an interactive calculator REPL (Read-Eval-Print Loop).

    Accepts one input per prompt. Calculations use the format '<operation> <a> <b>'.
    All errors are caught and printed; the loop continues until 'exit' is entered.
    Calls calculator.shutdown() on exit via a finally block.

    Commands:
        history: Print the current calculation history.
        save:    Persist history to disk.
        load:    Reload history from disk, replacing the current in-memory history.
        clear:   Clear the in-memory history without touching the history file.
        undo:    Revert the last calculation.
        redo:    Re-apply the last undone calculation.
        help:    List all commands and supported operations.
        exit:    Shut down the REPL.

    Args:
        calculator: The Calculator instance to use for all operations.

    Example:
        >>> start_repl(calculator)
        >>> add 5 3
        Result: 8.0
    """

    startscreen = Figlet(font="slant")
    print(startscreen.renderText("Calculator REPL"))
    print("Type 'exit' to quit.")
    print("Enter an operation and two numbers, or 'exit' to quit.")
    print("Enter 'help' to see available operations or 'history' to see previously ran operations.")

    try:
        while True:
            user_input = input("\n>>> ")
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
            elif user_input == "load":
                calculator.clear_history()
                calculator.load_history()
                print("History has been reloaded.")
                continue
            elif user_input == "undo":
                if calculator.undo():
                    print("History has been undone.")
                else:
                    print("Nothing to undo.")
                continue
            elif user_input == "redo":
                if calculator.redo():
                    print("History has been redone.")
                else:
                    print("Nothing to redo.")
                continue
            elif user_input == "help":
                print("Available Commands:")
                print("1. help\n2. save\n3. clear\n4. load\n5. redo\n6. undo\n7. exit\n")
                print("Available Operations:")
                for i, k in enumerate(calculator.get_supported_operations(), start=1):
                    print(f"{i}. {k}")
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
        