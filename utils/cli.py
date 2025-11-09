import click
from utils.logger import prune_logs

@click.group()
def cli():
    """Utility commands for Flowcase."""
    pass

@cli.command()
@click.option('--days', default=90, help='Number of days to retain logs (default: 90).')
def prune_logs_cmd(days):
    """Prune log entries older than the specified number of days."""
    try:
        prune_logs(days)
        click.echo(f"Successfully pruned logs older than {days} days.")
    except Exception as e:
        click.echo(f"Error pruning logs: {e}")

if __name__ == '__main__':
    cli()