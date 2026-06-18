# TLS Certificate Analyzer

Small Python CLI tool for inspecting TLS/X.509 certificates for domains.

It:

- connects to a host via TLS,
- retrieves the server certificate,
- parses X.509 with `cryptography`,
- calculates days until expiration,
- shows results in a colorized table using `rich`.

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

Example output:

```text
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃       Domain         ┃  Status  ┃ Days Left  ┃               Issuer                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│      example.com     │   OK     │     42     │ C=US, O=Let's Encrypt, CN=R10        │
└──────────────────────┴──────────┴────────────┴──────────────────────────────────────┘
```

Colors are applied only in the terminal; in plain text they look like regular strings.

### Multiple domains from file

Create a text file with one domain per line, for example:

```text
example.com
google.com
expired.badssl.com
```

Run:

```bash
python certcheck.py --input-file domains.txt
```

You will see a progress bar and then a table with all domains.

---

## CLI interface

```bash
python certcheck.py [OPTIONS] [DOMAIN]
```

**Arguments:**

- `DOMAIN` (optional)  
  Single domain to analyze, e.g. `example.com`.

**Options:**

- `--input-file`, `-i PATH`  
  Path to a `.txt` file with domains (one per line).

**Rules:**

- You must provide **either** `DOMAIN` **or** `--input-file`.
- Providing both at the same time is not allowed; the tool will fail with a clear parameter error.

---

## Output fields

For each domain the tool prepares a result dict with:

- `domain`
- `status` – `OK`, `EXPIRING`, `EXPIRED`, or `ERROR`
- `subject`
- `issuer`
- `serial_number`
- `not_before`
- `not_after`
- `days_left`
- `san`

Right now the table displays:

- **Domain**
- **Status** (colorized: green/yellow/red)
- **Days Left**
- **Issuer**

The remaining fields are available in the internal data and can be reused later (for JSON output, logging, etc.).

---

## Implementation overview

### Fetching the certificate

`fetch_certificate(domain, port=443)`:

- creates a TLS context via `ssl.create_default_context()`,
- opens a TCP connection with `socket.create_connection((domain, port), timeout=5)`,
- wraps it using `context.wrap_socket(sock, server_hostname=domain)`,
- calls `getpeercert(binary_form=True)` and returns the DER bytes.

### Parsing the certificate

`parse_certificate(cert_der)`:

- converts DER bytes into an `x509.Certificate` via  
  `cryptography.x509.load_der_x509_certificate(cert_der)`.

### Analyzing the certificate

`analyze_certificate(domain)`:

- fetches and parses the certificate,
- extracts subject, issuer, serial number, validity period,
- tries to read the `SubjectAlternativeName` (SAN) extension and collect DNS names,
- computes `days_left` from `not_valid_after_utc`,
- derives a status:
  - `EXPIRED` if `days_left < 0`,
  - `EXPIRING` if `0 <= days_left <= 30`,
  - `OK` otherwise,
- returns a dictionary with all collected fields.

### Rendering the table

`render_results_table(results)`:

- builds a `rich.table.Table`,
- adds columns for domain, status, days left, and issuer,
- applies simple color formatting to the status column,
- prints the table to the terminal.

---

## Error handling

The tool does not stop on a single failing domain:

- If certificate fetching fails (network/TLS error), the error is printed to stderr and the domain gets an `ERROR` row via a helper `error_result(domain)`.
- If parsing fails (invalid or malformed certificate), the error is also printed and the domain gets an `ERROR` row.

This way all domains from the input are still visible in the final table, with problematic ones clearly marked as `ERROR`.

## License

This project is licensed under the MIT License – see the LICENSE file for details.
