import click

from yag import (
    install as yag_install,
    remove as yag_remove,
    run as yag_run,
    scan as yag_scan,
    search as yag_search,
)

from pathlib import Path

SOURCE_SEP = ','


@click.group()
def cli():
    pass


@cli.command()
@click.argument("title", required=True)
@click.option("--host", required=False, default="127.0.0.1")
def search(title, host):
    yag_search(title, host)
    return 0


@cli.command()
@click.argument("title", required=True)
@click.option("--host", required=False, default="127.0.0.1")
@click.option("--source", required=False, default=None)
@click.option("--debug", required=False, default=False, is_flag=True)
def install(title, host, source, debug):
    if source:
        if SOURCE_SEP in source:
            source = [Path(s.strip()) for s in source.split(SOURCE_SEP)]
        else:
            source = Path(source)
    yag_install(title, host, source, debug)
    return 0


@cli.command()
@click.argument("title", required=True)
@click.option("--host", required=False, default="127.0.0.1")
@click.option("--debug", required=False, default=False, is_flag=True)
def run(title, host, debug):
    yag_run(title, host, debug)
    return 0


@cli.command()
@click.argument("source", required=True)
def scan(source):
    print(vars(yag_scan(Path(source))))
    return 0


@cli.command()
@click.argument("title", required=True)
@click.option("--host", required=False, default="127.0.0.1")
@click.option("--debug", required=False, default=False, is_flag=True)
def remove(title, host, debug):
    yag_remove(title, host, debug)
    return 0


if __name__ == '__main__':
    cli()
