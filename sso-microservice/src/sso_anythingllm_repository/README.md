# AnythingLLM Repository

A comprehensive async REST API client for AnythingLLM with support for GET, POST, DELETE, PUT, and PATCH methods with configurable arguments.

## Features

- **Async HTTP Client**: Built on `httpx.AsyncClient` for high-performance async HTTP requests
- **Configurable Arguments**: Support for custom URLs, headers, timeouts, and retry logic
- **Comprehensive Error Handling**: Custom exceptions for different error scenarios
- **Retry Logic**: Exponential backoff with configurable retry attempts
- **Context Manager Support**: Proper resource management with async context managers
- **Type Safety**: Full type hints and validation with Pydantic
- **Convenience Methods**: Pre-built methods for common AnythingLLM operations

## Installation

The repository is part of the SSO AnythingLLM microservice. Install dependencies:

```bash
cd sso-microservice/src/sso_anythingllm_repository
pip install -e .
```

## Quick Start

```python
import asyncio
from sso_anythingllm_repository import AnythingLLMRepository, AnythingLLMConfig

async def main():
    # Configure the repository
    config = AnythingLLMConfig(
        base_url="http://localhost:3001",
        api_key="your-api-key-here",
        timeout=30,
        max_retries=3
    )
    
    # Use as async context manager
    async with AnythingLLMRepository(config) as repo:
        # GET request
        workspaces = await repo.get("/api/v1/workspaces")
        
        # POST request
        new_workspace = await repo.post("/api/v1/workspaces", 
                                      json_data={"name": "Test Workspace"})
        
        # DELETE request
        await repo.delete(f"/api/v1/workspaces/{workspace_id}")

asyncio.run(main())
```

## Configuration

### AnythingLLMConfig

The configuration class supports the following parameters:

```python
from sso_anythingllm_repository import AnythingLLMConfig

config = AnythingLLMConfig(
    base_url="http://localhost:3001",      # Required: Base URL of AnythingLLM API
    api_key="your-api-key",                # Optional: API key for authentication
    timeout=30,                            # Optional: Request timeout in seconds
    max_retries=3,                         # Optional: Maximum retry attempts
    headers={                              # Optional: Custom headers
        "X-Custom-Header": "value"
    }
)
```

## API Methods

### Basic HTTP Methods

#### GET Request
```python
# Simple GET request
workspaces = await repo.get("/api/v1/workspaces")

# GET request with query parameters
workspace = await repo.get("/api/v1/workspaces/123", 
                          params={"include": "documents"})
```

#### POST Request
```python
# POST with JSON data
new_workspace = await repo.post("/api/v1/workspaces", 
                               json_data={"name": "New Workspace"})

# POST with form data
result = await repo.post("/api/v1/upload", 
                        data={"file": "content"})
```

#### DELETE Request
```python
# DELETE request
result = await repo.delete("/api/v1/workspaces/123")

# DELETE with parameters
result = await repo.delete("/api/v1/workspaces/123", 
                          params={"force": "true"})
```

#### PUT Request
```python
# PUT request for full updates
updated = await repo.put("/api/v1/workspaces/123", 
                        json_data={"name": "Updated Name"})
```

#### PATCH Request
```python
# PATCH request for partial updates
patched = await repo.patch("/api/v1/workspaces/123", 
                          json_data={"description": "New description"})
```

### Convenience Methods

The repository includes convenience methods for common AnythingLLM operations:

```python
# Workspace operations
workspaces = await repo.get_workspaces()
workspace = await repo.get_workspace("123")
created = await repo.create_workspace({"name": "Test"})
await repo.delete_workspace("123")

# Document operations
documents = await repo.get_documents("workspace_id")
uploaded = await repo.upload_document("workspace_id", document_data)
```

## Error Handling

The repository provides custom exceptions for different error scenarios:

```python
from sso_anythingllm_repository.exceptions import (
    AnythingLLMRepositoryError,
    NetworkError,
    AuthenticationError
)

try:
    result = await repo.get("/api/v1/workspaces")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except AnythingLLMRepositoryError as e:
    print(f"Repository error: {e}")
```

### Exception Types

- **AnythingLLMRepositoryError**: Base exception for repository errors
- **NetworkError**: Network-related errors (timeouts, connection failures)
- **AuthenticationError**: Authentication and authorization errors
- **ValidationError**: Data validation errors
- **ConfigurationError**: Configuration-related errors

## Advanced Usage

### Concurrent Requests

```python
async with AnythingLLMRepository(config) as repo:
    # Make multiple concurrent requests
    tasks = [
        repo.get("/api/v1/workspaces"),
        repo.get("/api/v1/system/health"),
        repo.get("/api/v1/system/info")
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Custom Headers

```python
config = AnythingLLMConfig(
    base_url="http://localhost:3001",
    api_key="your-key",
    headers={
        "X-Custom-Header": "custom-value",
        "User-Agent": "MyApp/1.0"
    }
)
```

### Retry Logic

The repository implements exponential backoff retry logic:

```python
config = AnythingLLMConfig(
    base_url="http://localhost:3001",
    max_retries=5,  # Will retry up to 5 times
    timeout=30
)
```

## Testing

Run the test suite:

```bash
cd sso-microservice/src/sso_anythingllm_repository
pytest tests/ -v
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `usage_example.py`: Basic and advanced usage patterns
- Error handling examples
- Concurrent request examples

## Architecture

The repository follows a clean architecture pattern:

```
sso_anythingllm_repository/
├── anything_llm_repository.py    # Main repository implementation
├── config.py                     # Configuration classes
├── exceptions.py                 # Custom exceptions
├── interfaces/                   # Protocol definitions
├── tests/                       # Test suite
└── examples/                    # Usage examples
```

## Dependencies

- `httpx`: Async HTTP client
- `pydantic`: Data validation and settings management
- `asyncio`: Async/await support
- `logging`: Logging functionality

## Contributing

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass

## License

This project is part of the SSO AnythingLLM microservice and follows the same licensing terms. 