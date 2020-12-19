import json
import os
import platform

from pathlib import Path

from typing import (
    List,
    Union,
)

from acme.library.utils.source import (
    get,
    Source,
)

from ansible.cli.playbook import PlaybookCLI

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/'
os.chdir(Path(BASE_PATH) / "acme")


def json_serializer(o):
    if isinstance(o, Path):
        return str(o)


def append_host(cmd_args: List[str], host: str) -> None:
    if host in ["localhost", "127.0.0.1"]:
        cmd_args.append("-c=local")
    cmd_args.append(f"-i {host},")


def search(name: str, host: str) -> None:
    return "TODO"


def install(name: str, host: str, source: Union[List[Path], Path], debug: bool = False) -> None:
    extra_vars = {
        "app_name": name,
        "source_path": source
    }
    if platform.system() == 'Linux':
        extra_vars["ansible_python_interpreter"] = "/usr/bin/python3"

    cmd_args = [
        "ansible-playbook",
        "install.yml",
        "--extra-vars",
        json.dumps(extra_vars, default=json_serializer)
    ]
    append_host(cmd_args, host)
    if debug:
        cmd_args.append("-vvvvv")
    cli = PlaybookCLI(args=cmd_args)
    assert (cli.run() == 0)


def run(name: str, host: str, debug: bool = False) -> None:
    extra_vars = {
        "app_name": name
    }
    cmd_args = [
        "ansible-playbook",
        "run.yml",
        "--extra-vars",
        json.dumps(extra_vars, default=json_serializer)
    ]
    append_host(cmd_args, host)
    if debug:
        cmd_args.append("-vvvvv")
    cli = PlaybookCLI(args=cmd_args)
    assert (cli.run() == 0)


def scan(source: Path) -> Source:
    return get(source)


def remove(name: str, host: str, debug: bool = False) -> None:
    extra_vars = {
        "app_name": name
    }
    cmd_args = [
        "ansible-playbook",
        "remove.yml",
        "--extra-vars",
        json.dumps(extra_vars, default=json_serializer)
    ]
    append_host(cmd_args, host)
    if debug:
        cmd_args.append("-vvvvv")
    cli = PlaybookCLI(args=cmd_args)
    assert (cli.run() == 0)
