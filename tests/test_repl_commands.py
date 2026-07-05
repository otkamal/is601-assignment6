import pytest
from app.repl_commands import ReplCmdFactory, ReplCmd

def test_duplicate_registration() -> None:
    with pytest.raises(ValueError, match="help is already registered"):
        @ReplCmdFactory.register_command('help')
        class FlimFlamCmd(ReplCmd):
            def execute(self) -> float:
                return 0
