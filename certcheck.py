import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
import ssl
import socket
from cryptography import x509
from datetime import datetime, timezone

console = Console()
err_console = Console(stderr=True)

def error_result(domain: str) -> dict:
    return {
        "domain": domain,
        "status": "ERROR",
        "subject": "N/A",
        "issuer": "N/A",
        "serial_number": "N/A",
        "not_before": "N/A",
        "not_after": "N/A",
        "days_left": "N/A",
        "san": "N/A",
    }

def parse_certificate(cert_der: bytes) -> x509.Certificate:
    return x509.load_der_x509_certificate(cert_der)

def fetch_certificate(domain: str, port: int = 443) -> bytes:
    """
    Fetch the TLS/X.509 certificate for a given domain.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as s:
                cert_der = s.getpeercert(binary_form=True)
        return cert_der
    except Exception as e:
        err_console.print(f"[red]Error fetching certificate for {domain}: {e}[/red]")
        return b""

def format_status(status: str) -> str:
    styles = {
        "OK": "[green]OK[/green]",
        "EXPIRING": "[yellow]EXPIRING[/yellow]",
        "EXPIRED": "[red]EXPIRED[/red]",
        "ERROR": "[red]ERROR[/red]",
    }
    return styles.get(status, status)

def analyze_certificate(domain: str) -> dict:
    """
    Fetch and analyze the TLS/X.509 certificate for a given domain.
    """
    cert_der = fetch_certificate(domain)

    if not cert_der:
        return error_result(domain)

    try:
        cert = parse_certificate(cert_der)
    except Exception as e:
        err_console.print(f"[red]Error parsing certificate for {domain}: {e}[/red]")
        return error_result(domain)

    try:
        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)            
        san_list = san_ext.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        san_list = []
        
    now = datetime.now(timezone.utc)
    days_left = (cert.not_valid_after_utc - now).days

    if days_left < 0:
        status = "EXPIRED"
    elif days_left <= 30:
        status = "EXPIRING"
    else:
        status = "OK"

    result = {
        "domain": domain,
        "status": status,
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_number": str(cert.serial_number),
        "not_before": cert.not_valid_before_utc.isoformat(),
        "not_after": cert.not_valid_after_utc.isoformat(),
        "days_left": str(days_left),
        "san": ", ".join(san_list) if san_list else "-",
    }

    return result

def render_results_table(results: list[dict]) -> None:
    table = Table(title="Certificate Analysis Results")

    table.add_column("Domain", style="cyan", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Days Left", justify="center")
    table.add_column("Issuer", style="magenta", justify="left")

    for result in results:
        table.add_row(
            result["domain"],
            format_status(result["status"]),
            result["days_left"],
            result["issuer"]
        )

    console.print(table)

def main(
    domain: str | None = typer.Argument(None, help="Single domain to analyze"),
    input_file: str | None = typer.Option(None, "--input-file", "-i", help="Read domains from .txt file")
) -> None:
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
        with open(input_file, "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f.readlines() if line.strip()]
        for d in track(domains, description="Analyzing certificates..."):
            results.append(analyze_certificate(d))

    render_results_table(results)


if __name__ == "__main__":
    typer.run(main)