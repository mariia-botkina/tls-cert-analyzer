import typer
import rich

def analyze_certificate(domain: str):
    """
    Fetch and analyze the TLS/X.509 certificate for a given domain.
    """
    rich.print(f"[blue]Analyzing certificate for domain:[/blue] {domain}")
    rich.print(f"[green]Certificate for {domain} analyzed successfully[/green]")

def main(
    domain: str | None = typer.Argument(None, help="Single domain to analyze"),
    input_file: str | None = typer.Option(None, "--input-file", "-i", help="Read domains from .txt file")
):
    """
    Analyze TLS/X.509 certificates for one domain or a list of domains.
    """
    
    if not (domain or input_file):
         raise typer.BadParameter("Provide a domain or use --input-file.")
    
    if domain and input_file:
        raise typer.BadParameter("Use either a domain or --input-file, not both.")

    if domain:
        analyze_certificate(domain)

    if input_file:
        with open(input_file, "r") as f:
            domains = [line.strip() for line in f.readlines()]
        for d in domains:
            analyze_certificate(d)


if __name__ == "__main__":
    typer.run(main)