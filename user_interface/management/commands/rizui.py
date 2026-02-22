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
    "/add-thread": "Create a new thread with a main statement.",
    "/show-thread": "Show details of a specific thread, including its main statement. Alias: /st",
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
    table.add_column("Created At", style="yellow")

    for idx, thread in enumerate(threads, start=1):
        table.add_row(
            str(idx),
            str(thread.get("id")),
            str(thread.get("created_at")),
        )

    console.print(table)


def create_thread_interaction(api_url: str) -> None:
    statement = Prompt.ask("Main Statement")
    if not statement.strip():
        console.print("[yellow]Statement cannot be empty.[/yellow]")
        return

    try:
        # Create the thread
        thread_resp = requests.post(f"{api_url}/api/statement/threads")
        thread_resp.raise_for_status()
        thread_data = thread_resp.json()
        thread_id = thread_data.get("id")

        # Create the main statement
        stmt_resp = requests.post(
            f"{api_url}/api/statement/threads/{thread_id}/statements",
            json={"content": statement, "is_main": True},
        )
        stmt_resp.raise_for_status()

        console.print(
            f"[bold green]Successfully created thread {thread_id} with the main statement.[/bold green]"
        )
    except Exception as e:
        console.print(f"[bold red]Failed to create thread or statement: {e}[/bold red]")


def show_thread(api_url: str, thread_id: str) -> None:
    try:
        thread_resp = requests.get(f"{api_url}/api/statement/threads/{thread_id}")
        if thread_resp.status_code == 404:
            console.print(f"[red]Thread {thread_id} not found.[/red]")
            return
        thread_resp.raise_for_status()
        thread_data = thread_resp.json()

        stmts_resp = requests.get(
            f"{api_url}/api/statement/threads/{thread_id}/statements"
        )
        stmts_resp.raise_for_status()
        statements = stmts_resp.json()
    except Exception as e:
        console.print(f"[bold red]Failed to fetch thread details: {e}[/bold red]")
        return

    main_statement = next((s for s in statements if s.get("is_main")), None)

    table = Table(title=f"Thread {thread_data.get('id')} Details", show_header=False)
    table.add_column("Key", style="cyan", justify="right")
    table.add_column("Value", style="magenta")

    table.add_row("Chat ID", str(thread_data.get("chat")))
    table.add_row("Created At", str(thread_data.get("created_at")))
    console.print(table)

    if main_statement:
        console.print(
            f"\n[bold cyan]Main Statement:[/bold cyan] {main_statement.get('content')}"
        )
        console.print(f"[dim]Created At: {main_statement.get('created_at')}[/dim]")
    else:
        console.print("\n[yellow]No main statement found for this thread.[/yellow]")

    other_statements = [s for s in statements if not s.get("is_main")]
    if other_statements:
        console.print("\n[bold]Other Statements:[/bold]")
        for stmt in other_statements:
            content = stmt.get("content")
            if len(content) > 60:
                content = content[:57] + "..."
            console.print(f" - {content} [dim](ID: {stmt.get('id')})[/dim]")
    console.print()


def configure_llms_on_startup(api_url: str) -> None:
    try:
        response = requests.get(f"{api_url}/api/configuration/llm-config")
        response.raise_for_status()
        configs = response.json()
        if configs:
            # Configurations already exist, skip prompting
            return
    except Exception as e:
        console.print(
            f"[bold red]Failed to check existing LLM configurations: {e}[/bold red]"
        )
        return

    console.print("[bold yellow]LLM Configuration required.[/bold yellow]")
    default_model = Prompt.ask("Enter the default LLM model name you want to use")

    if not default_model.strip():
        console.print("[yellow]Skipping configuration.[/yellow]")
        return

    tool_model = default_model
    reasoning_model = default_model

    separate = Prompt.ask(
        "Do you want to set separate models for TOOL_CALLING_LLM_MODEL and REASONING_LLM_MODEL?",
        choices=["y", "n"],
        default="n",
    )
    if separate.lower() == "y":
        tool_model = Prompt.ask("Enter TOOL_CALLING_LLM_MODEL", default=default_model)
        reasoning_model = Prompt.ask("Enter REASONING_LLM_MODEL", default=default_model)

    try:
        for name, value in [
            ("tool_calling_llm_model", tool_model),
            ("reasoning_llm_model", reasoning_model),
        ]:
            resp = requests.post(
                f"{api_url}/api/configuration/llm-config",
                json={"name": name, "value": value},
            )
            resp.raise_for_status()

        console.print("[bold green]LLM Configuration saved successfully![/bold green]")
        console.print("\n[bold cyan]Next Steps for LLM Authentication:[/bold cyan]")
        console.print(
            "Please create a [bold].env[/bold] file with the required environment "
            "variables to make LLM authentication work properly."
        )
        console.print("Since this app uses [bold]litellm[/bold], almost every LLM model and provider is supported.")
        console.print("To learn what environment variables to set for your chosen model, please visit:")
        console.print("[link=https://docs.litellm.ai/#basic-usage]https://docs.litellm.ai/#basic-usage[/link]\n")
    except Exception as e:
        console.print(f"[bold red]Failed to save LLM configuration: {e}[/bold red]")


@click.command()
@click.option(
    "--api-url",
    type=str,
    default="http://127.0.0.1:8000",
    help="Base URL of the backend API.",
)
def command(api_url: str) -> None:
    """A sample CLI command for rizui."""
    configure_llms_on_startup(api_url)

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
                elif cmd == "/add-thread":
                    create_thread_interaction(api_url)
                elif cmd.startswith("/show-thread") or cmd.startswith("/st"):
                    parts = cmd.split(" ", 1)
                    if len(parts) == 2 and parts[1].strip():
                        show_thread(api_url, parts[1].strip())
                    else:
                        console.print(
                            "[yellow]Please provide a Thread ID. Usage: /show-thread <ID>[/yellow]"
                        )
                elif cmd in ("/quit", "/exit"):
                    console.print("[bold green]Goodbye![/bold green]")
                    sys.exit(0)
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
            else:
                console.print(
                    "[yellow]Commands must start with '/'. Type /help for a list of commands.[/yellow]"
                )

        except KeyboardInterrupt, EOFError:
            console.print("\n[bold green]Goodbye![/bold green]")
            sys.exit(0)
