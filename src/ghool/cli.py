import click


@click.group()
@click.option(
    "--token",
    required=True,
    envvar="GITHUB_TOKEN",
    help="GitHub token (e.g. personal access token).\nAlso read from GITHUB_TOKEN.",
    metavar="TOKEN",
)
@click.pass_context
def main(ctx: click.Context, token: str) -> None:
    ctx.obj = {"token": token}


def import_commands():
    import importlib
    import pkgutil

    import ghool.commands as gc

    for _, name, _ in pkgutil.iter_modules(gc.__path__):
        module = importlib.import_module(f"{gc.__name__}.{name}")
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, click.Command):
                main.add_command(obj)


import_commands()
