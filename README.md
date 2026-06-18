# TLS Certificate Analyzer

A small Python CLI tool that analyzes TLS/X.509 certificates for domains.

It can:

- Connect to a domain via TLS.
- Retrieve the server certificate.
- Parse the X.509 certificate using `cryptography`.
- Calculate how many days are left until expiration.
- Show results in a nice colored table using Rich.

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

### Analyze a single domain

```bash
python certcheck.py example.com
```

You will see a table like:

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃           Domain             ┃   Status   ┃ Days Left  ┃           Issuer            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│          example.com         │    OK      │    42      │ C=US, O=Let's Encrypt, ...  │
└───────────────────────────────┴────────────┴────────────┴──────────────────────────────┘
```

Status is colorized:

- `OK` – green
- `EXPIRING` (≤ 30 days) – yellow
- `EXPIRED` / `ERROR` – red

### Analyze multiple domains from a file

Prepare a text file with domains, one per line, for example:

```text
example.com
google.com
expired.badssl.com
```

Run:

```bash
python certcheck.py --input-file domains.txt
```

The tool will show a progress bar and then a table with all results.

---

## CLI arguments

```bash
python certcheck.py [DOMAIN] --input-file PATH
```

- `DOMAIN` (positional, optional)  
  Single domain to analyze.

- `--input-file`, `-i` (optional)  
  Path to a `.txt` file with domains (one per line).

Rules:

- You must provide **either** a single `DOMAIN` **or** `--input-file`.
- Using both at the same time is not allowed; the tool will fail with a clear parameter error.

---

## How it works (overview)

### 1. Fetching the certificate

`fetch_certificate(domain, port=443)`:

- Creates a default TLS context (`ssl.create_default_context()`).
- Opens a TCP connection with `socket.create_connection((domain, port), timeout=5)`.
- Wraps the socket with TLS using `context.wrap_socket(sock, server_hostname=domain)`.
- Calls `getpeercert(binary_form=True)` to get the server certificate in DER (binary) form.

On success it returns `bytes` (DER certificate). On failure it logs an error and returns an empty `bytes` object.

### 2. Parsing the certificate

`parse_certificate(cert_der)`:

- Uses `cryptography.x509.load_der_x509_certificate(cert_der)` to turn DER bytes into an `x509.Certificate` object.

If parsing fails, `analyze_certificate()` returns an error result.

### 3. Analyzing the certificate

`analyze_certificate(domain)`:

- Calls `fetch_certificate(domain)`.
- If fetching fails (empty bytes), returns a standard `ERROR` result via `error_result(domain)`.
- Parses the certificate with `parse_certificate()`.
- Tries to read the `SubjectAlternativeName` (SAN) extension and collect DNS names.
- Computes `days_left` as `(not_valid_after_utc - now).days`.
- Derives a status:
  - `EXPIRED` – if `days_left < 0`
  - `EXPIRING` – if `0 ≤ days_left ≤ 30`
  - `OK` – otherwise
- Returns a dictionary with all relevant fields.

Returned fields:

- `domain` – input domain
- `status` – `OK` / `EXPIRING` / `EXPIRED` / `ERROR`
- `subject` – subject DN as a string
- `issuer` – issuer DN as a string
- `serial_number` – serial number as string
- `not_before` – start of validity (ISO string)
- `not_after` – end of validity (ISO string)
- `days_left` – days until expiration (string)
- `san` – comma-separated SAN DNS names or `"-"` if none

### 4. Rendering the results

`render_results_table(results)`:

- Builds a `rich.table.Table` with columns:
  - **Domain**
  - **Status**
  - **Days Left**
  - **Issuer**
- Uses `format_status(status)` to colorize the `status` cell based on its value.
- Prints the table using `Console.print()`.

---

## Error handling

- Network or TLS errors during fetch:
  - Printed to stderr via `err_console`.
  - The domain gets an `ERROR` row via `error_result(domain)`.

- Parsing errors (invalid/malformed certificate data):
  - Printed to stderr.
  - The domain also gets an `ERROR` row.

In both cases, the tool doesn’t crash; it just marks problematic domains in the table with `ERROR` and placeholder fields.

---

## Possible future improvements

Some ideas you can add later:

- CLI option to show `not_after` or `subject` in the table.
- `--port` option to scan non‑standard HTTPS ports.
- Exit codes:
  - e.g. return non‑zero if any domain is `ERROR` or `EXPIRED` (useful for CI).
- Optional JSON output for scripts (`--json`).

## License

This project is licensed under the MIT License – see the LICENSE file for details.
