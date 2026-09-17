# Assignment 4 - Sales Analytics MCP Server

## Overview

This project implements a local **Model Context Protocol (MCP) server** in Python for querying and analyzing a fictional sales dataset stored in SQLite.

The project was created for **ENGMT 5405 Assignment 4** to demonstrate how an AI assistant such as Claude Desktop can interact with an external data source through a controlled set of MCP tools and prompts.

Claude Desktop does not receive direct or unrestricted access to the SQLite database. Instead, Claude communicates with the local Python MCP server, which validates requests, applies security controls, executes approved database operations, and returns structured results.

The project demonstrates:

- Model Context Protocol (MCP) server development
- MCP tools and prompts
- Claude Desktop integration
- SQLite database access
- Input sanitization
- Parameterized SQL queries
- Allowlist-based query controls
- Rate limiting
- Security exploit testing
- Virtual environment management with uv
- Environment-based configuration
- Git/GitHub source control

---

## Domain

**Data Analysis**

The MCP server is designed to support simple sales-data analysis.

The fictional dataset contains:

- Order date
- Product
- Product category
- Sales region
- Units sold
- Revenue

The dataset was created specifically for this assignment and does not come from an external company, API, website, or production database.

The data is generated locally using:

```text
seed_database.py
```

and stored in:

```text
data/sales.db
```

The generated SQLite database is intentionally excluded from GitHub because it can be recreated at any time using the seed script.

---

## MCP Implementation

This project implements the assignment option:

```text
Two MCP Tools + One MCP Prompt
```

The MCP server is defined in:

```text
server.py
```

The server exposes the following functionality to Claude Desktop.

---

## Tool 1: `filter_sales`

The `filter_sales` tool returns individual sales records based on optional filters.

Supported inputs:

- `region`
- `category`
- `limit`

Example request:

> Show me Electronics sales in the North region.

A corresponding tool call may use:

```text
region = North
category = Electronics
limit = 10
```

Before querying the database, the server:

1. Applies rate limiting.
2. Sanitizes the region input.
3. Sanitizes the category input.
4. Validates the requested row limit.
5. Passes the validated values to the database layer.
6. Returns structured matching records.

Claude therefore does not construct or execute SQL directly.

---

## Tool 2: `sales_summary`

The `sales_summary` tool returns aggregated sales information.

It supports grouping by:

- `region`
- `category`
- `product`

Example request:

> Summarize total units and total revenue by region.

A corresponding tool input is:

```text
group_by = region
```

The tool returns:

- Total units
- Total revenue

for each group.

Only explicitly supported grouping fields are accepted.

---

## Prompt: `analyze_sales`

The `analyze_sales` MCP prompt provides reusable instructions for analyzing the sales dataset.

The prompt accepts a focus such as:

```text
regional sales performance
```

It instructs Claude to:

- Use the available MCP sales tools when appropriate
- Identify important sales patterns
- Compare stronger and weaker segments
- Discuss both units sold and revenue
- Base numerical conclusions on data returned by the tools
- Avoid inventing unsupported sales values
- Mention relevant dataset limitations
- Produce a concise and clearly structured analysis

The prompt itself does not directly query the SQLite database.

Instead, it guides Claude on how to use the available tools and interpret the returned results.

---

## Project Structure

```text
assignment4-mcp/
├── .env.example
├── .gitignore
├── .python-version
├── README.md
├── claude_desktop_config.json
├── database.py
├── pyproject.toml
├── requirements.txt
├── security.py
├── seed_database.py
├── server.py
├── test_security.py
├── uv.lock
├── data/
└── src/
```

---

## Main Files

- `server.py` — Defines the MCP server, two MCP tools, and one MCP prompt.
- `database.py` — Handles SQLite connections, filtering, aggregation, parameterized queries, and allowed grouping fields.
- `security.py` — Implements input sanitization, numeric validation, and rate limiting.
- `seed_database.py` — Creates the fictional SQLite database and inserts 20 sample sales records.
- `test_security.py` — Tests safe input, malicious input, invalid limits, and rate limiting.
- `claude_desktop_config.json` — Contains the Claude Desktop MCP configuration.
- `.env.example` — Documents the environment variables used by the project.
- `.gitignore` — Excludes the local environment, virtual environment, generated database, and other local files.
- `requirements.txt` — Lists the required Python packages.
- `pyproject.toml` — Contains the Python/uv project configuration.
- `uv.lock` — Locks dependency versions for reproducible development.

---

## Requirements

The project uses:

- Python 3.14+
- uv
- MCP Python SDK 2.2.0
- python-dotenv 1.2.3
- SQLite
- Claude Desktop

Node.js/npm may also be required to use MCP Inspector during development.

The Python dependencies are listed in:

```text
requirements.txt
```

with:

```text
mcp[cli]==2.2.0
python-dotenv==1.2.3
```

---

# Setup Instructions

## 1. Clone the Repository

Clone the private repository:

```bash
git clone https://github.com/keziamally/engmt5405-assignment4-mcp.git
```

Move into the project directory:

```bash
cd engmt5405-assignment4-mcp
```

Because the repository is private, GitHub access must first be granted by the repository owner.

---

## 2. Create a Virtual Environment

Create a virtual environment using uv:

```bash
uv venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

The virtual environment is stored in:

```text
.venv/
```

and is intentionally excluded from GitHub.

---

## 3. Install Dependencies

Install the project dependencies:

```bash
uv pip install -r requirements.txt
```

The dependencies are also represented in `pyproject.toml` and `uv.lock`.

---

## 4. Configure Environment Variables

Create a local `.env` file using `.env.example` as the template.

The project uses:

```text
DATABASE_PATH=data/sales.db
RATE_LIMIT_CALLS=5
RATE_LIMIT_WINDOW_SECONDS=60
```

The `.env` file is intentionally excluded from GitHub.

This allows environment-specific configuration to remain local.

---

## 5. Create the Sample Database

Run:

```bash
uv run python seed_database.py
```

The script:

1. Creates the required data directory.
2. Creates the SQLite database.
3. Creates the sales table.
4. Inserts 20 fictional sales records.

The resulting database is:

```text
data/sales.db
```

Because generated `.db` files are excluded from Git, the seed script should be run after cloning the repository.

---

# Database Access

The database access logic is implemented in:

```text
database.py
```

The file provides two main functions:

```text
filter_sales()
summarize_sales()
```

---

## Filtering Sales

The filtering operation supports:

```text
region
category
limit
```

Filter values are passed into SQLite using parameterized queries.

For example:

```sql
WHERE region = ?
```

The actual user-supplied value is passed separately from the SQL statement.

This helps prevent user input from being interpreted as executable SQL.

---

## Aggregation Allowlist

The summary operation accepts a grouping field.

Only the following values are allowed:

```text
region
category
product
```

The server rejects other fields before constructing the query.

This is important because SQL identifiers such as column names cannot be parameterized in the same way as normal SQL values.

---

# Security Best Practices

This project implements two required best practices:

1. **Input Sanitization**
2. **Rate Limiting**

---

## Best Practice 1: Input Sanitization

The input validation logic is implemented in:

```text
security.py
```

User-controlled text passes through the `sanitize_filter_text()` function before being passed to the database layer.

The validation:

- Ensures the input is a string
- Removes unnecessary surrounding whitespace
- Enforces a maximum length
- Allows only expected characters
- Rejects unsupported or suspicious punctuation

Allowed characters include:

- Letters
- Numbers
- Spaces
- Underscores
- Hyphens

For example:

```text
North
```

is accepted.

An injection-style value such as:

```text
North' OR 1=1 --
```

is rejected because it contains unsupported characters.

The malicious input is blocked before it can be used in a database query.

---

## Numeric Validation

The `filter_sales` tool also validates the requested row limit.

The allowed range is:

```text
1 to 100
```

For example:

```text
limit = 20
```

is valid.

A request such as:

```text
limit = 500
```

is rejected.

---

## Additional SQL Protection

The project uses multiple layers of protection for database operations.

These include:

- Input sanitization
- Parameterized SQL for filter values
- Numeric validation
- A strict allowlist for aggregation fields

This reduces the ability of user input to alter the intended SQL behavior.

---

## Best Practice 2: Rate Limiting

The project implements an in-memory sliding-window rate limiter.

The default configuration is:

```text
RATE_LIMIT_CALLS=5
RATE_LIMIT_WINDOW_SECONDS=60
```

This limits repeated calls to protected MCP operations within the configured period.

If the maximum number of requests is exceeded, the server returns:

```text
Rate limit exceeded. Please try again later.
```

The rate limiter stores recent request timestamps for each operation and removes timestamps once they fall outside the configured time window.

The rate-limit history resets when the local MCP server process restarts.

---

# Security and Exploit Testing

Security tests are implemented in:

```text
test_security.py
```

Run the tests using:

```bash
uv run python test_security.py
```

The tests cover:

- Normal valid input
- SQL-injection-style input
- Invalid numeric limits
- Excessive repeated requests

Expected output includes:

```text
Running security tests...

[PASS] Normal filter input accepted
[PASS] Injection-style input blocked
[PASS] Invalid row limit blocked
[PASS] Rate limit triggered correctly

All security tests passed.
```

---

## Input Sanitization Exploit Test

Example malicious input:

```text
North' OR 1=1 --
```

The expected behavior is for the request to be rejected because unsupported characters are detected.

Another malicious grouping value is:

```text
region; DROP TABLE sales;--
```

This input is rejected.

An unsupported grouping value such as:

```text
order_date
```

is also rejected because it is not part of the approved grouping allowlist.

A normal query can still be executed afterward to confirm that the database continues to operate.

---

## Rate-Limit Exploit Test

The second exploit demonstration repeatedly calls a protected operation within the configured rate-limit window.

The default configuration allows:

```text
5 requests per 60 seconds
```

Once the permitted request count is exceeded, an additional request is blocked.

This demonstrates that excessive repeated tool calls are prevented by the server.

---

# Error Handling

The MCP tools return controlled validation errors rather than exposing raw stack traces or internal implementation details.

For example:

```text
region contains unsupported characters.
```

or:

```text
Rate limit exceeded. Please try again later.
```

Database connections are also closed using `try/finally` so that resources are released after each database operation.

---

# MCP Inspector Testing

The MCP server can be tested locally using MCP Inspector.

Run:

```bash
uv run mcp dev server.py
```

The Inspector should display:

```text
Tools
├── filter_sales
└── sales_summary

Prompts
└── analyze_sales
```

---

## Example `filter_sales` Test

Use:

```text
region = North
category = Electronics
limit = 10
```

The server should return matching Electronics records for the North region.

---

## Example `sales_summary` Test

Use:

```text
group_by = region
```

The server should return total units and total revenue grouped by region.

---

## Example `analyze_sales` Prompt Test

Use:

```text
regional sales performance
```

as the analysis focus.

The MCP prompt should return structured instructions explaining how Claude should use the available tools and analyze the results.

---

# Claude Desktop Integration

The MCP server has been configured and tested with Claude Desktop.

The connector appears as:

```text
Kezia Sales Analytics
```

The repository includes:

```text
claude_desktop_config.json
```

which contains the MCP configuration used by Claude Desktop.

The configuration specifies:

- The uv executable
- The MCP package version
- The local `server.py` path
- The database path
- The rate-limit settings

The current configuration contains machine-specific absolute paths.

These paths must be updated when running the server on a different computer.

---

## Installing the MCP Server in Claude Desktop

From the project directory, the MCP SDK can register the local server using:

```bash
uv run mcp install server.py --name "Kezia Sales Analytics" -f .env
```

After installation, completely quit and restart Claude Desktop so the configuration is reloaded.

---

# Claude Desktop Testing

The MCP integration was tested successfully using both tools.

## Example 1

User request:

> Using my Kezia Sales Analytics tools, show me Electronics sales in the North region.

Claude uses:

```text
filter_sales
```

and returns the matching records.

---

## Example 2

User request:

> Using my Kezia Sales Analytics tools, summarize total units and total revenue by region.

Claude uses:

```text
sales_summary
```

and returns aggregated regional results.

These tests verify that Claude Desktop can discover and call the locally implemented MCP tools.

---

# MCP Prompt in Claude Desktop

The `analyze_sales` prompt is also exposed through the MCP connector.

It appears as:

```text
Analyze sales
```

under the `Kezia Sales Analytics` MCP connection.

This confirms that the server exposes the required:

```text
2 tools + 1 prompt
```

configuration.

---

# Configuration and Secret Management

The project stores local configuration in:

```text
.env
```

The `.env` file is excluded from Git.

A reproducible example is provided in:

```text
.env.example
```

The `.gitignore` file excludes:

```text
.env
.venv/
data/*.db
__pycache__/
.vscode/
.DS_Store
```

The project uses `pathlib.Path` to construct the local database path.

No external authenticated API is used by this project, so no API key or external service credential is required.

---

# Reproducing the Dataset

The sales dataset is fictional and was created specifically for this assignment.

It contains 20 sample records representing:

- Electronics
- Furniture
- Multiple products
- Four sales regions
- Units sold
- Revenue

To recreate the database at any time, run:

```bash
uv run python seed_database.py
```

This allows the project to remain reproducible without committing the generated SQLite database.

---

# Code Citation

The basic MCP server structure and the use of MCP tool and prompt registration were adapted from the official **Model Context Protocol Python SDK** documentation and examples:

```text
https://github.com/modelcontextprotocol/python-sdk
```

The source is also cited directly in a comment in `server.py`, as required by the assignment.

The assignment-specific database logic, sales dataset, security controls, rate limiter, MCP tool behavior, analysis prompt, and tests were implemented specifically for this project.

---

# Quick Start

After cloning and entering the project directory:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run python seed_database.py
uv run python test_security.py
```

To test the MCP server with MCP Inspector:

```bash
uv run mcp dev server.py
```

To install the server in Claude Desktop:

```bash
uv run mcp install server.py --name "Kezia Sales Analytics" -f .env
```

---

# Summary

This project demonstrates how the Model Context Protocol can provide a controlled interface between an AI assistant and a local data source.

Claude Desktop interacts with the sales dataset only through the capabilities exposed by the Python MCP server:

```text
filter_sales
sales_summary
analyze_sales
```

The server validates user input, applies rate limiting, performs controlled database operations, and returns structured results.

The project therefore includes:

- A working Python MCP server
- Two distinct MCP tools
- One MCP prompt
- SQLite database integration
- Claude Desktop integration
- Input sanitization
- Rate limiting
- Exploit demonstrations
- Automated security tests
- Environment-based configuration
- Reproducible setup instructions
- Source-code citation