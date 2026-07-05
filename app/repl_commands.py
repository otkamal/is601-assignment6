import logging
from abc import ABC, abstractmethod
from app.calculator import Calculator
from colorama import Fore, init, Style
from app.exceptions import ReplExit


class ReplCmd(ABC):

    """
    Abstract base class representing a single REPL command.

    Command pattern: each REPL request (history, save, undo, a calculation, ...)
    is encapsulated as a ReplCmd instance so the REPL loop can dispatch to it
    without needing to know how it's implemented.

    Attributes:
        description: One-line summary shown by HelpCmd.

    Methods:
        execute(calculator, args): Performs the command's action.
    """

    description: str = ""

    def __init__(self):
        """Initialize the command. Subclasses currently carry no state of their own."""
        pass

    @abstractmethod
    def execute(self, calculator: Calculator, args: list[str]) -> None:
        """
        Performs the command's action against the given calculator.

        Args:
            calculator: The Calculator instance to act on.
            args: Remaining tokens from the user's input line, after the
                command name itself has been consumed by the caller.
        """
        pass #PRAGMA: NO COVER

class ReplCmdFactory:

    """
    Factory for registering and instantiating ReplCmd subclasses.

    Subclasses are registered via the register_command decorator and
    retrieved by name through build_cmd.

    Methods:
        register_command(cmd): Decorator to register a ReplCmd subclass.
        build_cmd(cmd): Instantiates a registered ReplCmd by name.
        get_supported_cmds(): Returns the names of all registered commands.
    """

    _cmds = {}

    @classmethod
    def register_command(cls, cmd: str):
        """
        Decorator that registers a ReplCmd subclass under the given name.

        Args:
            cmd: The command name to register (case-insensitive).

        Returns:
            A decorator that registers the decorated class and returns it unchanged.

        Raises:
            ValueError: If the command name is already registered.
        """
        def registration_decorator(subclass):
            cmd_sanitized = cmd.lower()
            if cmd_sanitized in cls._cmds:
                raise ValueError(f"{cmd_sanitized} is already registered")
            cls._cmds[cmd_sanitized] = subclass
            return subclass
        return registration_decorator

    @classmethod
    def build_cmd(cls, cmd: str):
        """
        Instantiates a registered ReplCmd by name.

        Args:
            cmd: The command name (case-insensitive).

        Returns:
            A ReplCmd instance ready to be executed.

        Raises:
            ValueError: If the command name is not registered.
        """
        cmd_sanitized = cmd.lower()
        if cmd_sanitized not in cls._cmds:
            raise ValueError(f"{cmd_sanitized} is not a registered operation")
        new_cmd = cls._cmds.get(cmd_sanitized)
        return new_cmd()

    @classmethod
    def get_supported_cmds(cls):
        """
        Returns the names of all registered commands.

        Returns:
            A view of the registered command name strings.
        """
        return cls._cmds.keys()

@ReplCmdFactory.register_command('history')
class HistoryCmd(ReplCmd):

    """Command that prints the calculator's current calculation history."""

    description = "Show previously run calculations."

    def execute(self, calculator, args):
        """Print each calculation in history, numbered, or a message if empty."""
        history = calculator.get_history()
        if not history:
            print(Fore.YELLOW + "No history yet.")
        else:
            for i, calc in enumerate(history, start=1):
                print(Fore.CYAN + f"{i}. " + Fore.YELLOW + f"{calc}")


@ReplCmdFactory.register_command('save')
class SaveCmd(ReplCmd):

    """Command that persists the in-memory history to disk."""

    description = "Persist history to disk."

    def execute(self, calculator, args):
        """Save history to the configured history file."""
        calculator.save_history()
        print(Fore.GREEN + "History saved to disk.")

@ReplCmdFactory.register_command('clear')
class ClearCmd(ReplCmd):

    """Command that clears in-memory history without touching the history file."""

    description = "Clear the in-memory history without touching the history file."

    def execute(self, calculator, args):
        """Clear the calculator's in-memory history."""
        calculator.clear_history()
        print(Fore.GREEN + "History has been cleared.")

@ReplCmdFactory.register_command('load')
class LoadCmd(ReplCmd):

    """Command that reloads history from disk, replacing what's in memory."""

    description = "Reload history from disk, replacing the current in-memory history."

    def execute(self, calculator, args):
        """Clear in-memory history and reload it from the history file."""
        calculator.clear_history()
        calculator.load_history()
        print(Fore.GREEN + "History has been reloaded.")

@ReplCmdFactory.register_command('undo')
class UndoCmd(ReplCmd):

    """Command that reverts the most recent calculation."""

    description = "Revert the last calculation."

    def execute(self, calculator, args):
        """Undo the last calculation, or report there is nothing to undo."""
        if calculator.undo():
            print(Fore.GREEN + "History has been undone.")
        else:
            print(Fore.YELLOW + "Nothing to undo.")

@ReplCmdFactory.register_command('redo')
class RedoCmd(ReplCmd):

    """Command that re-applies the most recently undone calculation."""

    description = "Re-apply the last undone calculation."

    def execute(self, calculator, args):
        """Redo the last undone calculation, or report there is nothing to redo."""
        if calculator.redo():
            print(Fore.GREEN + "History has been redone.")
        else:
            print(Fore.YELLOW + "Nothing to redo.")

@ReplCmdFactory.register_command('help')
class HelpCmd(ReplCmd):

    """Command that lists all registered REPL commands and supported operations."""

    description = "List all commands and supported operations."

    def execute(self, calculator, args):
        """Print a table of commands (with descriptions) and a grid of operations."""
        print(Fore.YELLOW + "Available Commands:" + Style.RESET_ALL)
        names = sorted(ReplCmdFactory.get_supported_cmds())
        name_width = max(len(name) for name in names)
        for name in names:
            description = ReplCmdFactory._cmds[name].description
            print(f"  {Fore.CYAN}{name.ljust(name_width)}{Style.RESET_ALL}  {description}")

        print()
        print(Fore.YELLOW + "Available Operations:" + Style.RESET_ALL)
        operations = sorted(calculator.get_supported_operations())
        op_width = max(len(op) for op in operations)
        per_row = 4
        for i in range(0, len(operations), per_row):
            row = operations[i:i + per_row]
            print("  " + "  ".join(f"{Fore.CYAN}{op.ljust(op_width)}{Style.RESET_ALL}" for op in row))

@ReplCmdFactory.register_command('exit')
class ExitCmd(ReplCmd):

    """Command that shuts down the REPL loop."""

    description = "Shut down the REPL."

    def execute(self, calculator, args):
        """Print a goodbye message and signal the REPL loop to stop.

        Raises:
            ReplExit: Always, to unwind the REPL loop's dispatch try/except.
        """
        print(Fore.LIGHTBLUE_EX + "Exiting calculator... Goodbye ~")
        raise ReplExit()

class CalculateCmd(ReplCmd):

    """Command that runs a calculator operation. The REPL's fallback when the
    first token isn't a registered command name; not itself registered under
    a fixed keyword since operation names live in CalculationFactory."""

    description = "Run a calculator operation, e.g. 'add 5 3'."

    def execute(self, calculator, args):
        """Parse args as (operation, a, b), run the calculation, and print the result.

        Args:
            calculator: The Calculator instance to run the operation on.
            args: A 3-item list: [operation, operand_a, operand_b].
        """
        try:
            operation, a, b = args
            a, b = float(a), float(b)
            result = calculator.calculate(operation, a, b).result
            print(Fore.GREEN + "Result: " + Style.BRIGHT + f"{result}")
        except ValueError as e:
            logging.error(e)
            print(Fore.RED + "Error: " + Style.BRIGHT + f"{e}")
        except ZeroDivisionError as e:
            logging.error(e)
            print(Fore.RED + Style.BRIGHT + f"Error: {e}")
