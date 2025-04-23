# Documentation & Project TODO

This list tracks planned improvements and tasks for the OARC-Crawlers project and its documentation.

## Documentation Tasks

-   **[~] API Docs for `core`, `utils`, `config`:** Add detailed API documentation in `API.md` for modules within these directories once their interfaces stabilize.
-   **[ ] Advanced Usage Examples:** Create more complex examples in `examples/` demonstrating combined workflows (e.g., research workflow, code comparison).
-   **[ ] Configuration Guide:** Add a dedicated section or document explaining all configuration options (file & environment variables) in detail.
-   **[ ] Deployment Guide:** Add notes on deploying the MCP server or running crawlers in production environments (e.g., Docker, task queues).
-   **[X] Contribution Guide:** Create `CONTRIBUTING.md` outlining how others can contribute (code style, tests, PR process).
-   **[X] Update Mermaid Diagrams:** Ensure all diagrams in `Crawlers.md` and `Specification.md` accurately reflect the current implementation.

## Core Implementation Tasks

-   **[X] Implement `utils.paths`:** Fully integrate a robust path management class/module (`utils/paths.py`) across all components for handling data/config/cache directories consistently based on OS and configuration.
-   **[~] Complete Test Coverage:** Write comprehensive unit and integration tests (`tests/`) for all core crawler modules, utilities, and CLI commands. Aim for high code coverage.
-   **[ ] Build out `api` package:** Define and implement clear interfaces or wrappers for external APIs used by crawlers, potentially within the `src/oarc_crawlers/api/` directory.
-   **[ ] Implement `core.manager.Manager`:** Create a central `Manager` class to orchestrate crawler tasks, potentially handling initialization, configuration injection, and routing calls from CLI/API layers to core modules.
-   **[ ] Implement `serve` package/command:** Develop a dedicated command (`oarc-crawlers serve`) using a web framework (e.g., FastAPI, Flask) to provide an HTTP API alternative/complement to the MCP server.
-   **[ ] Filesystem Crawler:** Add a new crawler component capable of indexing and extracting metadata/content from local filesystem directories.
-   **[X] Refine Error Handling:** Standardize error types and reporting across all modules for consistency.
-   **[X] Secure Credential Management:** Implement secure handling for API keys or other credentials (e.g., using environment variables, keyring, or a dedicated secrets management solution). Avoid hardcoding or storing in plain text config files.
-   **[ ] Dependency Review:** Regularly review and update dependencies listed in `pyproject.toml`.