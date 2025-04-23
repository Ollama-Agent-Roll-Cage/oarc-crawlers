# OARC-Crawlers Troubleshooting Guide

This guide provides solutions to common issues you might encounter when installing or using OARC-Crawlers.

## Table of Contents
- [Virtual Environment Issues](#virtual-environment-issues)
- [Installation Problems](#installation-problems)
- [Dependency Conflicts](#dependency-conflicts)
- [Runtime Errors](#runtime-errors)
- [Platform-Specific Issues](#platform-specific-issues)
- [CLI & API Issues](#cli--api-issues)
- [MCP & VS Code Integration](#mcp--vs-code-integration)
- [Getting Help](#getting-help)

## Virtual Environment Issues

### Python venv Cleanup and Management

A clean Python environment is essential. Use `uv` for best results.

```bash
# List installed packages
pip list

# Example output (minimal, clean venv)
# oarc-crawlers 0.1.2
# pip           25.0.1
# setuptools    78.1.0
# wheel         0.45.1

# Install uv if missing
pip install uv

# Deactivate any conda/venv
conda deactivate || true
.venv\Scripts\deactivate || true

# Remove all packages except pip/setuptools/wheel
pip freeze | Select-String -Pattern "^(?!pip)" | ForEach-Object { pip uninstall -y $_.ToString().Trim() }

# Re-activate and check
.venv\Scripts\activate
pip list
```

### Virtual Environment Isolation Issues

If you see unexpected packages or conflicts, check your Python path:

```bash
which python  # Unix/MacOS
where python  # Windows

# Should point to your venv, not system Python.
# If not, deactivate/reactivate or recreate the venv.
```

## Installation Problems

### Package Not Found Errors

- Check your internet connection.
- Upgrade pip and uv:
  ```bash
  pip install --upgrade pip uv
  ```
- Try both `uv pip install oarc-crawlers` and `pip install oarc-crawlers`.

### Permission Issues

- **Windows:** Run PowerShell as administrator.
- **Unix/MacOS:** Use `sudo` if needed.

### Version Compatibility

- OARC-Crawlers requires Python 3.10 or 3.11.
- Check your version:
  ```bash
  python --version
  ```
- If not 3.10/3.11, create a new venv:
  ```bash
  uv venv --python 3.11
  ```

## Dependency Conflicts

- Always use a clean venv.
- If you see dependency errors, try:
  ```bash
  uv pip install oarc-crawlers==<latest_version>
  ```
- Avoid mixing system and venv packages.

## Runtime Errors

### YouTube Download Issues

- Update oarc-crawlers (`uv pip install -U oarc-crawlers`).
- Check the video URL and regional restrictions.
- Use `--verbose` for more error details.
- If you see "Video unavailable" or "No streams found", try a different video or check for age/content restrictions.

### Web Crawler Connection Problems

- Check your internet connection.
- Some sites block bots; try setting a user-agent:
  ```python
  headers = {'User-Agent': 'Mozilla/5.0'}
  crawler = WebCrawler(data_dir="./data", headers=headers)
  ```
- For SSL errors, update your Python and CA certificates.

### GitHub API Rate Limiting

- Use authenticated requests if possible.
- Wait and retry if rate-limited.
- Cache results to avoid repeated requests.

### ArXiv/Other API Issues

- If you get "Paper not found" or "API error", check the arXiv ID or query.
- For "Too many requests", wait and retry.

## Platform-Specific Issues

### Windows

- Path length limits: keep data directories short.
- PowerShell execution policy: run `Set-ExecutionPolicy RemoteSigned` if needed.
- File locking: close files before re-running commands.

### MacOS

- SSL errors: update Python and run `Install Certificates.command` if needed.
- XCode tools may be required for some dependencies.

### Linux

- Install build essentials (`sudo apt install build-essential`).
- Use `uv` to avoid system package conflicts.

## CLI & API Issues

### CLI Command Not Found

- Ensure your venv is activated.
- On Windows, check that `%USERPROFILE%\AppData\Roaming\Python\Scripts` is in your PATH.
- Try `python -m oarc_crawlers` as a fallback.

### CLI Usage Errors

- Use `oarc-crawlers --help` and `oarc-crawlers [command] --help` for options.
- For argument errors, check the [Cheat Sheet](CHEATSHEET.md) or [CLI.md](CLI.md).

### API Import/Usage Errors

- Use correct imports:
  ```python
  from oarc_crawlers import YTCrawler, GHCrawler, ArxivCrawler, DDGCrawler, WebCrawler
  ```
- All async methods must be awaited inside an `async def` function.
- Use `asyncio.run(...)` to run top-level async code.

### Data/Parquet Issues

- If you see "Parquet file not found" or "cannot read file", check the path and permissions.
- Use `oarc-crawlers data view <file>` to inspect Parquet files.

## MCP & VS Code Integration

### MCP Server Not Starting

- Ensure port 3000 is free or specify `--port`.
- Use `oarc-crawlers mcp run --verbose` for debug output.

### VS Code Can't Connect

- Check your MCP server config in VS Code settings:
  ```json
  {
    "mcp.servers": [
      { "name": "OARC Crawlers", "port": 3000, "transport": "ws" }
    ]
  }
  ```
- Make sure the MCP server is running before starting VS Code.

### MCP/Agent Errors

- Errors are returned as structured JSON with `error.code` and `error.message`.
- See [VSCodeMCP.md](VSCodeMCP.md) for error code meanings.

## Getting Help

- Use `--verbose` for detailed logs.
- Check [docs/CHEATSHEET.md](CHEATSHEET.md) and [docs/Examples.md](Examples.md) for usage.
- For API reference: see [docs/API.md](API.md).
- For unresolved issues:
  1. Search [GitHub Issues](https://github.com/Ollama-Agent-Roll-Cage/oarc-crawlers/issues)
  2. Open a new issue with error details, OS, Python version, and steps to reproduce.
