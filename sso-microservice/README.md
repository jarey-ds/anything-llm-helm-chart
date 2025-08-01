## Documentation

- [REST API Documentation](src/artemis_model_catalogue_rest/docs/API_DOC.md): Overview and diagram of the REST API endpoints.
- [Application Architecture](docs/APP_ARCHITECTURE.md): Layered architecture and data flow of the application.
- [Database ERD Documentation](src/artemis_model_catalogue_entity/docs/DATABASE_ERD.md): Database Entity-Relationship diagram based on declared entities.

## What is offered:

- 🎯 Universal Model Access - One interface to rule them all
- 🔮 Provider Agnostic - OpenAI, Anthropic, Bedrock... you name them all
- 🛡️ Store user API keys

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Prerequisites

- Python 3.11+
- uv (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Getting Started

1. Clone the repository:

   ```bash
   git clone git@github.com:jarey-ds/anything-llm-helm-chart.git
   cd sso-microservice
   ```

3. Install dependencies (this also sets up pre-commit hooks):

   ```bash
   uv run task install
   ```

   Pre-commit hooks are automatically installed to ensure code quality checks run before commits and tests run before pushes.

4. Run the tests:

   ```bash
   uv run task test
   ```

5. Run linting:

   ```bash
   uv run task lint
   ```

6. Format code:
   ```bash
   uv run task format
   ```

### Running the Application

```bash
uv run task run
```

The API will be available at http://localhost:8000

### Common Commands

All commands are managed through taskipy.

#### Development Setup

- `task install` - Install all dependencies (including dev)
- `task install-prod` - Install only production dependencies
- `task cache-clean` - Clean uv cache
- `task run` - Run the API server

#### Code Quality

- `task lint` - Run ruff linting checks
- `task lint-fix` - Fix auto-fixable linting issues
- `task format` - Auto-format code with ruff (including imports)
- `task format-check` - Check formatting without applying changes
- `task check-all` - Run all checks (format, lint, tests)
- `task fix-all` - Fix all auto-fixable issues (format and lint)

#### Cleaning

- `task clean` - Remove all Python artifacts and test files
- `task clean-pyc` - Remove Python bytecode files
- `task clean-test` - Remove test artifacts

#### Testing

- `task test` - Run all tests
- `task test-unit` - Run unit tests only
- `task test-integration` - Run integration tests only
- `task test-cov` - Run tests with coverage report

#### Docker Operations

- `task docker-build` - Build Docker image
- `task docker-run` - Run Docker container
