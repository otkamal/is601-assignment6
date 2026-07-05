import readline
from colorama import Fore, init, Style
from pyfiglet import Figlet
import logging
from app.calculator import Calculator
from app.exceptions import ReplExit
from app.repl_commands import ReplCmdFactory, CalculateCmd


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

    init()
    startscreen = Figlet(font="slant")
    print(Fore.GREEN + startscreen.renderText("Calculator REPL"))
    print(Style.RESET_ALL)
    print("Enter an operation and two numbers, or 'exit' to quit.")
    print(Fore.YELLOW + "Enter 'help' to see available operations or 'history' to see previously ran operations.")

    try:
        while True: 

            print(Style.RESET_ALL)  
            user_input = input(Fore.LIGHTBLUE_EX + ">>> " + Style.RESET_ALL)
            user_input = user_input.lower()
            tokens = user_input.split()

            try:
                cmd = ReplCmdFactory.build_cmd(tokens[0])
                args = tokens[1:]
            except ValueError:
                cmd = CalculateCmd()
                args = tokens

            try:
                cmd.execute(calculator, args)
                continue
            except ReplExit:
                break  
  
    finally:
        calculator.shutdown()
