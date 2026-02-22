import sys

import djclick as click
import requests
from rich.console import Console
from rich.prompt import IntPrompt
from rich.table import Table

console = Console()


@click.command()
@click.option(
    "--api-url",
    type=str,
    default="http://127.0.0.1:8000",
    help="Base URL of the backend API.",
)
def command(api_url: str) -> None:
    """A sample CLI command for rizui."""
    try:
        response = requests.get(f"{api_url}/api/statement/threads")
        response.raise_for_status()
        threads = response.json()
    except Exception as e:
        console.print(f"[bold red]Failed to fetch threads from API: {e}[/bold red]")
        sys.exit(1)

    if not threads:
        console.print("[yellow]No threads found.[/yellow]")
        return

    table = Table(title="Available Threads")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Thread ID", style="magenta")
    table.add_column("Chat ID", style="green")
    table.add_column("Created At", style="yellow")

    for idx, thread in enumerate(threads, start=1):
        table.add_row(
            str(idx),
            str(thread.get("id")),
            str(thread.get("chat")),
            str(thread.get("created_at")),
        )

    console.print(table)

    choices = [str(i) for i in range(1, len(threads) + 1)]
    choice = IntPrompt.ask(
        "Select a thread to view", choices=choices, show_choices=False
    )

    selected_thread = threads[choice - 1]
    console.print(f"[bold blue]You selected Thread {selected_thread['id']}[/bold blue]")
