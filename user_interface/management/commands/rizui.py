import sys

import djclick as click
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

COMMANDS = {
    "/help": "Show a list of all available commands and a description of each.",
    "/threads": "Show a list of all available threads.",
    "/quit": "Exit the application.",
}


def show_help():
    table = Table(
        title="Available Commands", show_header=True, header_style="bold magenta"
    )
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")

    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)

    console.print(table)


def show_threads(api_url: str) -> None:
    try:
        response = requests.get(f"{api_url}/api/statement/threads")
        response.raise_for_status()
        threads = response.json()
    except Exception as e:
        console.print(f"[bold red]Failed to fetch threads from API: {e}[/bold red]")
        return

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


@click.command()
@click.option(
    "--api-url",
    type=str,
    default="http://127.0.0.1:8000",
    help="Base URL of the backend API.",
)
def command(api_url: str) -> None:
    """A sample CLI command for rizui."""
    console.print(
        "Type [bold cyan]/help[/bold cyan] to see a list of available commands."
    )

    while True:
        try:
            choice = Prompt.ask("Enter a command")

            if choice.startswith("/"):
                cmd = choice.strip()
                if cmd == "/help":
                    show_help()
                elif cmd == "/threads":
                    show_threads(api_url)
                elif cmd in ("/quit", "/exit"):
                    console.print("[bold green]Goodbye![/bold green]")
                    sys.exit(0)
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
            else:
                console.print(
                    "[yellow]Commands must start with '/'. Type /help for a list of commands.[/yellow]"
                )

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold green]Goodbye![/bold green]")
            sys.exit(0)
