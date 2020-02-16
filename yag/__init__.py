import json
import os

from pathlib import Path

from typing import (
    List,
    Union,
)

from acme.library.utils.source import (
    get,
    Source,
)

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/'
os.chdir(Path(BASE_PATH) / "acme")

from ansible.cli.playbook import PlaybookCLI


def json_serializer(o):
    if isinstance(o, Path):
        return str(o)


def search(name: str) -> None:
    print("aaaa")


def install(name: str, source: Union[List[Path], Path], debug=False) -> None:
    extra_vars = {
        "app_name": name,
        "source_path": source
    }
    cmd_args = [
        "ansible-playbook",
        "install.yml",
        "--extra-vars",
        json.dumps(extra_vars, default=json_serializer)
    ]
    if debug:
        cmd_args.append("-vvvvv")
    cli = PlaybookCLI(args=cmd_args)
    assert (cli.run() == 0)


def run(name: str, debug=False) -> None:
    extra_vars = {
        "app_name": name
    }
    #extra_vars["ansible_python_interpreter"] = "/usr/bin/python3.7"
    cmd_args = [
        "ansible-playbook",
        "run.yml",
        "--extra-vars",
        json.dumps(extra_vars, default=json_serializer)
    ]
    if debug:
        cmd_args.append("-vvvvv")
    cli = PlaybookCLI(args=cmd_args)
    assert (cli.run() == 0)


def scan(source: Path) -> Source:
    return get(source)
