# Assignment 4 - Sales Analytics MCP Server

## Overview

This project implements a local **Model Context Protocol (MCP) server** in Python for querying and analyzing a fictional sales dataset stored in SQLite.

The project was created for **ENGMT 5405 Assignment 4** to demonstrate how an AI assistant such as Claude Desktop can interact with an external data source through a controlled set of tools rather than receiving unrestricted access to the underlying database.

In this project, Claude Desktop does **not** connect directly to the SQLite database. Instead, Claude communicates with a local MCP server that exposes specific capabilities. The MCP server validates each request, applies security controls, queries the database when appropriate, and returns structured results to Claude.

At a high level, the system works as follows:

```text
User
  ↓
Claude Desktop
  ↓
Model Context Protocol (MCP)
  ↓
Python MCP Server
  ↓
Input Validation + Rate Limiting
  ↓
Database Functions
  ↓
SQLite Sales Database
  ↓
Structured Results
  ↓
Claude Desktop
  ↓
User
```

The project demonstrates:

- Model Context Protocol architecture
- MCP tool development
- MCP prompt development
- Claude Desktop integration
- SQLite database access
- Input validation and sanitization
- Parameterized SQL queries
- Allowlist-based query controls
- Rate limiting
- Automated security testing
- Virtual environment and dependency management
- Git/GitHub source control

---

## Domain

**Data Analysis**

The MCP server is designed to perform simple sales-data analysis.

The fictional dataset contains the following fields:

- Order date
- Product
- Product category
- Sales region
- Units sold
- Revenue

The data was created specifically for this assignment. It does **not** come from an external company, website, API, or production system.

A Python script called `seed_database.py` creates the dataset and stores it in a local SQLite database:

```text
data/sales.db
```

The generated `.db` file is intentionally excluded from GitHub because the database can be recreated at any time using the seed script.

---

## What the MCP Server Does

The MCP server acts as a controlled bridge between Claude Desktop and the sales database.

Claude can discover and use the functionality exposed by the server, but it cannot run arbitrary SQL or directly access the database.

The server exposes:

- Two MCP tools
- One MCP prompt

The selected assignment structure is therefore:

```text
2 Tools + 1 Prompt
```

---

## MCP Components

### Tool 1: `filter_sales`

The `filter_sales` tool returns individual sales records using optional filters.

Supported inputs are:

- `region`
- `category`
- `limit`

Example request from Claude:

> Show me Electronics sales in the North region.

A corresponding tool call may contain:

```text
region = North
category = Electronics
limit = 10
```

Before the database query runs, the server:

1. Applies rate limiting.
2. Validates the region input.
3. Validates the category input.
4. Validates the requested row limit.
5. Passes the validated values to the database layer.
6. Returns structured matching records.

This means Claude does not construct or execute SQL directly.

---

### Tool 2: `sales_summary`

The `sales_summary` tool produces aggregated sales information.

It can group the dataset by:

- `region`
- `category`
- `product`

Example request:

> Summarize total units and total revenue by region.

The corresponding tool input is:

```text
group_by = region
```

The database then calculates:

- Total units
- Total revenue

for each region.

Only the explicitly supported grouping fields are accepted.

---

### Prompt: `analyze_sales`

The `analyze_sales` MCP prompt provides reusable instructions for analyzing the sales dataset.

The prompt accepts a `focus`, such as:

```text
regional sales performance
```

It instructs Claude to:

- Use the available MCP sales tools when appropriate
- Identify important patterns
- Compare stronger and weaker segments
- Discuss both units sold and revenue
- Base numerical conclusions only on data returned by the tools
- Avoid inventing sales values or unsupported facts
- Mention limitations of the dataset
- Produce a concise and clearly structured analysis

The prompt itself does **not** directly access the database.

Instead, it guides the AI on how to reason about the problem and when to use the available tools.

---

## System Design

The project separates responsibilities across multiple Python files rather than placing all functionality in one file.

```text
Claude Desktop
      │
      │ MCP request
      ▼
   server.py
      │
      ├────────────── analyze_sales prompt
      │
      ▼
  security.py
      │
      ▼
  database.py
      │
      ▼
data/sales.db
```

### Why this separation is useful

`server.py` handles the MCP interface.

`security.py` handles validation and rate limiting.

`database.py` handles SQL and database access.

`seed_database.py` handles creation of the sample dataset.

This separation keeps the MCP layer, security logic, and database logic independent and easier to understand, test, and maintain.

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

- `server.py` — Defines the MCP server, the two MCP tools, and the analysis prompt.
- `database.py` — Handles SQLite connections, filtering queries, aggregation, parameterized SQL, and allowed grouping fields.
- `security.py` — Implements text sanitization, limit validation, and the in-memory rate limiter.
- `seed_database.py` — Creates the fictional SQLite sales database and inserts 20 sample sales records.
- `test_security.py` — Runs automated checks for input validation and rate limiting.
- `claude_desktop_config.json` — Contains the Claude Desktop MCP configuration.
- `.env.example` — Documents the environment variables required by the application.
- `.gitignore` — Prevents local environment files, virtual environments, and generated databases from being committed.
- `requirements.txt` — Lists the Python dependencies required to run the project.
- `pyproject.toml` — Contains the uv/Python project configuration.
- `uv.lock` — Locks dependency versions for reproducibility.

---

## Requirements

The project uses:

- Python 3.14+
- uv
- MCP Python SDK 2.2.0
- python-dotenv 1.2.3
- SQLite
- Claude Desktop

For MCP Inspector development and testing, Node.js/npm may also be required.

The Python dependencies are included in `requirements.txt`:

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

Create a Python virtual environment using uv:

```bash
uv venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

When activated, the terminal should indicate that the project virtual environment is active.

---

## 3. Install Dependencies

Install the project dependencies:

```bash
uv pip install -r requirements.txt
```

The dependencies are also represented in `pyproject.toml` and locked through `uv.lock`.

---

## 4. Configure Environment Variables

Create a local `.env` file using `.env.example` as the template.

The configuration used by this project is:

```text
DATABASE_PATH=data/sales.db
RATE_LIMIT_CALLS=5
RATE_LIMIT_WINDOW_SECONDS=60
```

The `.env` file is intentionally excluded from GitHub.

This avoids committing local configuration or sensitive values into source control.

---

## 5. Create the Local Sales Database

Run:

```bash
uv run python seed_database.py
```

The script creates the SQLite database and inserts the sample dataset.

The generated database is located at:

```text
data/sales.db
```

The database contains 20 fictional sales records.

Because `data/*.db` is ignored by Git, anyone cloning the repository should run the seed script before using the MCP server.

---

# Database Layer

The database is implemented using SQLite.

The database access code is located in:

```text
database.py
```

The file provides two main operations:

```text
filter_sales()
summarize_sales()
```

### Filtering

The filtering function supports:

```text
region
category
limit
```

Filter values are passed to SQLite using parameterized SQL.

For example:

```sql
WHERE region = ?
```

The actual user value is supplied separately from the SQL statement.

This reduces the possibility of user input being interpreted as SQL code.

---

## Aggregation Allowlist

The summary operation requires a column name to be inserted into a SQL grouping clause.

Because SQL identifiers such as column names cannot be handled in the same way as normal query values, the project uses an explicit allowlist.

Only the following values are accepted:

```text
region
category
product
```

Any other grouping value is rejected before the SQL query is constructed.

---

# Security Best Practices

The assignment requires two best practices to be implemented and demonstrated.

This project implements:

1. **Input Sanitization**
2. **Rate Limiting**

---

## Best Practice 1: Input Sanitization

The input validation logic is implemented in:

```text
security.py
```

Text values pass through `sanitize_filter_text()` before reaching the database.

The validation:

- Ensures the value is a string
- Removes surrounding whitespace
- Rejects overly long values
- Allows only letters, numbers, spaces, underscores, and hyphens
- Rejects unsupported or suspicious punctuation

For example, the following legitimate input is accepted:

```text
North
```

However, an injection-style value such as:

```text
North' OR 1=1 --
```

is rejected because it contains unsupported characters.

A rejected request returns a controlled error rather than querying the database.

---

## Numeric Input Validation

The `limit` argument is also validated.

The allowed range is:

```text
1 to 100
```

For example:

```text
limit = 20
```

is valid, while:

```text
limit = 500
```

is rejected.

---

## Additional SQL Protection

Input sanitization is not the only protection used.

The database layer also uses:

- Parameterized SQL for filter values
- An explicit allowlist for grouping columns

This provides multiple layers of protection around database access.

---

## Best Practice 2: Rate Limiting

The second best practice is rate limiting.

The server uses a simple in-memory sliding-window rate limiter.

The default configuration is:

```text
RATE_LIMIT_CALLS=5
RATE_LIMIT_WINDOW_SECONDS=60
```

This means each protected MCP operation is allowed a limited number of calls during a 60-second window.

If the limit is exceeded, the server rejects the request with:

```text
Rate limit exceeded. Please try again later.
```

The rate limiter stores recent request times for each operation and removes timestamps after they fall outside the configured window.

Because the implementation is in memory, its state resets when the server process is restarted.

---

# Security Testing

Automated tests are provided in:

```text
test_security.py
```

Run them with:

```bash
uv run python test_security.py
```

The script tests:

- Normal text input
- SQL-injection-style input
- Invalid row limits
- Rate limiting

Expected output includes:

```text
Running security tests...

[PASS] Normal filter input accepted
[PASS] Injection-style input blocked
[PASS] Invalid row limit blocked
[PASS] Rate limit triggered correctly

All security tests passed.
```

The test script uses an isolated rate limiter for testing so that it can demonstrate the blocking behavior without depending on the state of the live MCP server.

---

# MCP Inspector Testing

During development, the server can be tested using MCP Inspector.

Run:

```bash
uv run mcp dev server.py
```

The Inspector should expose:

```text
Tools
├── filter_sales
└── sales_summary

Prompts
└── analyze_sales
```

---

## Example Tool Test: `filter_sales`

Use:

```text
region = North
category = Electronics
limit = 10
```

The tool should return matching Electronics records for the North region.

---

## Example Tool Test: `sales_summary`

Use:

```text
group_by = region
```

The tool should return total units and total revenue grouped by region.

---

## Example Prompt Test: `analyze_sales`

Use a focus such as:

```text
regional sales performance
```

The MCP prompt should return structured instructions describing how the available tools should be used to analyze the dataset.

---

# Exploit Demonstration

The assignment also requires demonstrating that each implemented best practice blocks an exploit or misuse case.

## Input-Sanitization Exploit

Example malicious input:

```text
North' OR 1=1 --
```

The expected behavior is for the request to be rejected because the region contains unsupported characters.

A malicious grouping input such as:

```text
region; DROP TABLE sales;--
```

is also rejected.

An unsupported but non-malicious grouping value such as:

```text
order_date
```

is rejected because it is not included in the allowed grouping fields.

After an attempted malicious query, a valid query can still be executed to verify that the database remains intact.

---

## Rate-Limit Exploit

Repeatedly calling a protected tool within the configured time window eventually triggers the rate limit.

With the default configuration:

```text
5 requests / 60 seconds
```

additional requests during the same active window are rejected.

This demonstrates that the MCP server can prevent excessive repeated tool calls.

---

# Claude Desktop Integration

The MCP server was successfully connected to Claude Desktop.

The connector appears as:

```text
Kezia Sales Analytics
```

The project includes:

```text
claude_desktop_config.json
```

which documents the working MCP configuration.

The current configuration uses:

```text
/opt/homebrew/bin/uv
```

and points to the local `server.py` file.

Because file paths differ between computers, the absolute paths in the configuration must be updated when running the project on another machine.

---

## Installing the MCP Server in Claude Desktop

From the project directory, the MCP Python SDK can register the server with Claude Desktop using:

```bash
uv run mcp install server.py --name "Kezia Sales Analytics" -f .env
```

This creates the Claude Desktop MCP entry using the local server and environment configuration.

After installation, completely quit Claude Desktop and reopen it so the configuration is reloaded.

---

# Claude Desktop Testing

The MCP integration was tested from Claude Desktop using both tools.

## Example 1

User request:

> Using my Kezia Sales Analytics tools, show me Electronics sales in the North region.

Claude selected:

```text
filter_sales
```

and returned the matching sales records.

---

## Example 2

User request:

> Using my Kezia Sales Analytics tools, summarize total units and total revenue by region.

Claude selected:

```text
sales_summary
```

and returned aggregated regional results.

Claude then used those tool results to explain the relative sales performance of the regions.

This confirms the end-to-end flow:

```text
User
↓
Claude Desktop
↓
MCP Tool
↓
Python Server
↓
Security Checks
↓
SQLite Database
↓
Tool Result
↓
Claude Response
```

---

# MCP Prompt in Claude Desktop

The `analyze_sales` MCP prompt is also exposed to Claude Desktop.

It appears under the `Kezia Sales Analytics` connector as:

```text
Analyze sales
```

This confirms that the server successfully exposes both MCP tools and the required MCP prompt.

---

# Configuration and Secret Management

The project uses `.env` for local configuration.

The following files or directories are intentionally excluded from Git:

```text
.env
.venv/
data/*.db
__pycache__/
.vscode/
.DS_Store
```

A safe configuration template is provided as:

```text
.env.example
```

This allows another user to reproduce the expected environment without committing the local `.env` file.

---

# Reproducing the Database

The database can be recreated at any time using:

```bash
uv run python seed_database.py
```

This makes the repository reproducible without storing the generated SQLite database in source control.

The fictional data is defined in `seed_database.py`.

---

# Code Citation

The basic MCP server structure and the use of MCP tool and prompt registration were adapted from the official **Model Context Protocol Python SDK** documentation and examples:

```text
https://github.com/modelcontextprotocol/python-sdk
```

The attribution is also included directly as a comment in `server.py`.

The assignment-specific sales database, tool logic, validation logic, rate limiter, security tests, sample dataset, and analysis prompt were implemented specifically for this project.

---

# Quick Start

For an already configured machine, the main commands are:

```bash
cd engmt5405-assignment4-mcp
source .venv/bin/activate
uv pip install -r requirements.txt
uv run python seed_database.py
uv run python test_security.py
```

To launch MCP Inspector:

```bash
uv run mcp dev server.py
```

To install the server into Claude Desktop:

```bash
uv run mcp install server.py --name "Kezia Sales Analytics" -f .env
```

---

# Limitations

This project is intentionally small and designed for demonstration purposes.

Current limitations include:

- The dataset contains only 20 fictional records.
- The database is local and not connected to a live production data source.
- The rate limiter is stored in memory and resets when the MCP server restarts.
- The MCP tools support only a limited set of filters and aggregation fields.
- There is no persistent user authentication layer because the server is designed to run locally.
- The Claude Desktop configuration contains machine-specific absolute paths.
- The project does not implement advanced analytics or visualization.

These limitations keep the project small enough to demonstrate the MCP architecture clearly while still showing useful security and software-engineering practices.

---

# Possible Future Improvements

Possible extensions include:

- Connecting the MCP server to a larger or live dataset
- Adding date-range filtering
- Adding more sales-analysis tools
- Adding visualization capabilities
- Using persistent/shared rate-limit storage
- Adding authentication for a remotely hosted MCP server
- Adding more comprehensive automated tests
- Adding structured logging and monitoring
- Supporting more advanced statistical analysis

---

# Summary

This project demonstrates how the Model Context Protocol can provide a controlled interface between an AI assistant and an external data source.

Instead of giving Claude unrestricted database access, the system exposes a small set of explicit capabilities:

```text
filter_sales
sales_summary
analyze_sales
```

The Python MCP server controls how these capabilities operate.

Before database access occurs, the server validates inputs and applies rate limiting. Database queries are further protected through parameterized SQL and allowlisted grouping fields.

The completed project therefore demonstrates:

- A working local Python MCP server
- Two functional MCP tools
- One reusable MCP prompt
- SQLite integration
- Claude Desktop integration
- Input sanitization
- Rate limiting
- Exploit testing
- Reproducible project setup
- Clear separation between the AI client, MCP interface, security layer, and database layer