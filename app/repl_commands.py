import logging
from abc import ABC, abstractmethod
from app.calculator import Calculator
from colorama import Fore, init, Style
from app.exceptions import ReplExit


class ReplCmd(ABC):

    description: str = ""

    def __init__(self):
        pass

    @abstractmethod
    def execute(self, calculator: Calculator, args: list[str]) -> None:
        pass #PRAGMA: NO COVER

class ReplCmdFactory:

    _cmds = {}

    @classmethod
    def register_command(cls, cmd: str):
        def registration_decorator(subclass):
            cmd_sanitized = cmd.lower()
            if cmd_sanitized in cls._cmds:
                raise ValueError(f"{cmd_sanitized} is already registered")
            cls._cmds[cmd_sanitized] = subclass
            return subclass
        return registration_decorator
    
    @classmethod
    def build_cmd(cls, cmd: str):
        cmd_sanitized = cmd.lower()
        if cmd_sanitized not in cls._cmds:
            raise ValueError(f"{cmd_sanitized} is not a registered operation")
        new_cmd = cls._cmds.get(cmd_sanitized)
        return new_cmd()
    
    @classmethod
    def get_supported_cmds(cls):
        return cls._cmds.keys()

@ReplCmdFactory.register_command('history')
class HistoryCmd(ReplCmd):

    description = "Show previously run calculations."

    def execute(self, calculator, args):
        history = calculator.get_history()
        if not history:
            print(Fore.YELLOW + "No history yet.")
        else:
            for i, calc in enumerate(history, start=1):
                print(Fore.CYAN + f"{i}. " + Fore.YELLOW + f"{calc}")


@ReplCmdFactory.register_command('save')
class SaveCmd(ReplCmd):

    description = "Persist history to disk."

    def execute(self, calculator, args):
        calculator.save_history()
        print(Fore.GREEN + "History saved to disk.")

@ReplCmdFactory.register_command('clear')
class ClearCmd(ReplCmd):

    description = "Clear the in-memory history without touching the history file."

    def execute(self, calculator, args):
        calculator.clear_history()
        print(Fore.GREEN + "History has been cleared.")

@ReplCmdFactory.register_command('load')
class LoadCmd(ReplCmd):

    description = "Reload history from disk, replacing the current in-memory history."

    def execute(self, calculator, args):
        calculator.clear_history()
        calculator.load_history()
        print(Fore.GREEN + "History has been reloaded.")

@ReplCmdFactory.register_command('undo')
class UndoCmd(ReplCmd):

    description = "Revert the last calculation."

    def execute(self, calculator, args):
        if calculator.undo():
            print(Fore.GREEN + "History has been undone.")
        else:
            print(Fore.YELLOW + "Nothing to undo.")

@ReplCmdFactory.register_command('redo')
class RedoCmd(ReplCmd):

    description = "Re-apply the last undone calculation."

    def execute(self, calculator, args):
        if calculator.redo():
            print(Fore.GREEN + "History has been redone.")
        else:
            print(Fore.YELLOW + "Nothing to redo.")

@ReplCmdFactory.register_command('help')
class HelpCmd(ReplCmd):

    description = "List all commands and supported operations."

    def execute(self, calculator, args):
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

    description = "Shut down the REPL."

    def execute(self, calculator, args):
        print(Fore.LIGHTBLUE_EX + "Exiting calculator... Goodbye ~")
        raise ReplExit()

class CalculateCmd(ReplCmd):

    def execute(self, calculator, args):
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
