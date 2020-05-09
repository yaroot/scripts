import click
import subs.migrate
from subs.news import sankei, yomiuri, gendai
from subs.twr import fav, timeline

@click.group()
def cli(): pass

@cli.command()
def migrate(): subs.migrate.run(dry_run=False)

@cli.command()
def run_sankei(): sankei.main()

@cli.command()
def run_yomiuri(): yomiuri.main()

@cli.command()
def run_gendai(): gendai.main()


@cli.command()
@click.pass_context
def run_news(ctx):
    ctx.invoke(run_sankei)
    ctx.invoke(run_yomiuri)
    ctx.invoke(run_gendai)


@cli.command()
def run_fav_full(): fav.save_history()

@cli.command()
def run_fav(): fav.save_latest()

@cli.command()
def run_timeline(): timeline.main()


if __name__ == '__main__':
    cli()
