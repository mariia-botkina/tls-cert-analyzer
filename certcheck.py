import typer
import rich
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()
err_console = Console(stderr=True)

def analyze_certificate(domain: str):
    """
    Fetch and analyze the TLS/X.509 certificate for a given domain.
    """
    # Placeholder for certificate analysis logic
    # In a real implementation, this would involve fetching the certificate,
    # parsing it, and extracting relevant information.
    
    # Simulated result for demonstration purposes
    result = {
        "domain": domain,
        "issuer": "Example CA",
        "valid_from": "2023-01-01",
        "valid_to": "2024-01-01",
        "status": "Valid"
    }
    
    return result

def render_results_table(results: list[dict]) -> None:
    table = Table(title="Certificate Analysis Results")

    table.add_column("Domain", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Expires In", justify="right")

    for result in results:
        table.add_row(
            result["domain"],
            result["status"],
            result["valid_to"],
        )

    console.print(table)

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
    
    results = []

    if domain:
        results.append(analyze_certificate(domain))

    if input_file:
        with open(input_file, "r") as f:
            domains = [line.strip() for line in f.readlines()]
        for d in track(domains, description="Analyzing certificates..."):
            results.append(analyze_certificate(d))

    render_results_table(results)


if __name__ == "__main__":
    typer.run(main)