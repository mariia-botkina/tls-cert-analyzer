import typer
import rich

def main(
    domain: str | None = typer.Argument(None, help="Single domain to analyze"),
    input_file: str | None = typer.Option(None, "--input-file", "-i", help="Read domains from .txt file")
):
    """
    Analyze TLS/X.509 certificates for a domain or a list of domains.
    """
    
    if not (domain or input_file):
         raise typer.BadParameter("Define --domain or --input-file")
    
    if domain and input_file:
        raise typer.BadParameter("Use --domain or --input-file")

    if domain:
        pass

    if input_file:
        pass

    # rich.print("[green]Certificate analyzed successfully[/green]")


if __name__ == "__main__":
    typer.run(main)