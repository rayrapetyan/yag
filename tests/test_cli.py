from click.testing import CliRunner

from yag.cli import (
    search,
)

def test_search():
    runner = CliRunner()
    result = runner.invoke(search, ['machinar'])
    assert result.exit_code == 0
    #assert result.output == 'machinarium/gog\n'
