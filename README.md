# TLS Certificate Analyzer

Small Python CLI tool for inspecting TLS/X.509 certificates for domains.

- Connects to a host via TLS
- Retrieves the server certificate
- Parses X.509 with `cryptography`
- Calculates days until expiration
- Displays results in a table using `rich`

---

## Requirements

- Python 3.10+
- Packages:
  - `typer`
  - `rich`
  - `cryptography`

Install dependencies:

```bash
pip install typer rich cryptography
```

---

## Usage

Assume the script file is called `certcheck.py`:

```bash
python certcheck.py [OPTIONS] [DOMAIN]
```

### Single domain

```bash
python certcheck.py example.com
```

### Multiple domains from file

File `domains.txt`:

```text
example.com
google.com
expired.badssl.com
```

Run:

```bash
python certcheck.py --input-file domains.txt
```

---

## CLI arguments

- `DOMAIN` (positional, optional)  
  Single domain to analyze.

- `--input-file`, `-i PATH`  
  Path to a text file with domains, one per line.

Rules:

- Provide either `DOMAIN` or `--input-file`
- Using both at the same time is not allowed

---

## Output fields

For each domain the tool collects:

- `domain`
- `status` – `OK`, `EXPIRING`, `EXPIRED`, `ERROR`
- `subject`
- `issuer`
- `serial_number`
- `not_before`
- `not_after`
- `days_left`
- `san`

Currently the table shows:

- Domain
- Status (colorized)
- Days Left
- Issuer

---

## Implementation overview

- `fetch_certificate(domain, port=443)`  
  - Creates TLS context via `ssl.create_default_context()`
  - Opens TCP connection with `socket.create_connection`
  - Wraps it with `context.wrap_socket(..., server_hostname=domain)`
  - Calls `getpeercert(binary_form=True)` and returns DER bytes

- `parse_certificate(cert_der)`  
  - Uses `cryptography.x509.load_der_x509_certificate(cert_der)` to obtain an `x509.Certificate` object

- `analyze_certificate(domain)`  
  - Fetches and parses the certificate
  - Extracts subject, issuer, validity, SAN, serial number
  - Computes `days_left` and derives a high-level status

- `render_results_table(results)`  
  - Renders a `rich` table and applies simple color formatting to the status column

---

## Error handling

- Network/TLS errors while fetching:
  - Logged to stderr
  - Domain appears in the table with status `ERROR`

- Parsing errors:
  - Logged to stderr
  - Domain also appears with status `ERROR`

The tool does not stop on a single failing domain.

## License

This project is licensed under the MIT License – see the LICENSE file for details.
