# -*- coding: utf-8 -*-
import os
import sys
import click
import shutil

from .Maverick.Builder import Builder
from .Maverick.Config import g_conf

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
work_path = os.path.abspath('.')
root_path = os.path.abspath(os.path.dirname(__file__))
repo_default_dir_path = os.path.join(root_path, "default_dir")


@click.group(context_settings=CONTEXT_SETTINGS)
def repo_cli():
    pass


@repo_cli.command(name="create")
@click.argument("name")
def create(name):
    new_repo_path = os.path.join(work_path, name)
    click.echo(root_path)
    if os.path.exists(new_repo_path):
        click.echo("文件夹已经存在")
    else:
        shutil.copytree(repo_default_dir_path, new_repo_path)


@repo_cli.command(name="generate")
def generate():
    config_path = os.path.join(root_path, "Maverick/default_config.py")
    g_conf.update_from_file(config_path)
    click.echo(g_conf.mvrk_path)
    builder = Builder(g_conf)
    builder.build_all()


def main() -> None:
    repo_cli.main()


if __name__ == "__main__":
    main()

