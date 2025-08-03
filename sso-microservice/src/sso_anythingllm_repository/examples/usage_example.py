"""
Usage example for AnythingLLMRepository with async REST API client functionality.

This example demonstrates how to use the repository to interact with the AnythingLLM API
using various HTTP methods with configurable arguments.
"""

import asyncio
import logging

from sso_anythingllm_repository.anything_llm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig
from sso_anythingllm_repository.exceptions import AnythingLLMRepositoryError, AuthenticationError, NetworkError


async def basic_usage_example():
    """Basic usage example showing GET, POST, and DELETE operations"""

    # Configure the repository
    config = AnythingLLMConfig(base_url="http://localhost:3001", api_key="your-api-key-here", timeout=30, max_retries=3)

    # Use the repository as an async context manager
    async with AnythingLLMRepository(config) as repo:
        try:
            # GET request - fetch all workspaces
            print("Fetching workspaces...")
            workspaces = await repo.get("/api/v1/workspaces")
            print(f"Found {len(workspaces.get('workspaces', []))} workspaces")

            # POST request - create a new workspace
            print("\nCreating new workspace...")
            new_workspace_data = {"name": "Test Workspace", "description": "A test workspace created via API"}
            created_workspace = await repo.post("/api/v1/workspaces", json_data=new_workspace_data)
            workspace_id = created_workspace.get("id")
            print(f"Created workspace with ID: {workspace_id}")

            # GET request with parameters
            print(f"\nFetching workspace {workspace_id}...")
            workspace = await repo.get(f"/api/v1/workspaces/{workspace_id}")
            print(f"Workspace details: {workspace}")

            # DELETE request - remove the workspace
            print(f"\nDeleting workspace {workspace_id}...")
            delete_result = await repo.delete(f"/api/v1/workspaces/{workspace_id}")
            print(f"Delete result: {delete_result}")

        except AuthenticationError as e:
            print(f"Authentication error: {e}")
        except NetworkError as e:
            print(f"Network error: {e}")
        except AnythingLLMRepositoryError as e:
            print(f"Repository error: {e}")


async def advanced_usage_example():
    """Advanced usage example showing PUT, PATCH, and convenience methods"""

    config = AnythingLLMConfig(
        base_url="http://localhost:3001",
        api_key="your-api-key-here",
        timeout=30,
        max_retries=3,
        headers={"X-Custom-Header": "custom-value"},
    )

    async with AnythingLLMRepository(config) as repo:
        try:
            # Use convenience methods
            print("Using convenience methods...")

            # Get all workspaces using convenience method
            workspaces = await repo.get_workspaces()
            print(f"Workspaces: {workspaces}")

            # Create workspace using convenience method
            workspace_data = {"name": "Advanced Test Workspace"}
            created = await repo.create_workspace(workspace_data)
            workspace_id = created.get("id")
            print(f"Created workspace: {created}")

            # PUT request - full update
            print(f"\nUpdating workspace {workspace_id}...")
            update_data = {"name": "Updated Workspace Name", "description": "Updated description"}
            updated = await repo.put(f"/api/v1/workspaces/{workspace_id}", json_data=update_data)
            print(f"Updated workspace: {updated}")

            # PATCH request - partial update
            print(f"\nPatching workspace {workspace_id}...")
            patch_data = {"description": "Patched description"}
            patched = await repo.patch(f"/api/v1/workspaces/{workspace_id}", json_data=patch_data)
            print(f"Patched workspace: {patched}")

            # Get documents in workspace
            documents = await repo.get_documents(workspace_id)
            print(f"Documents in workspace: {documents}")

            # Upload document to workspace
            document_data = {"name": "test_document.pdf", "type": "pdf", "content": "base64_encoded_content_here"}
            uploaded = await repo.upload_document(workspace_id, document_data)
            print(f"Uploaded document: {uploaded}")

            # Clean up - delete workspace
            await repo.delete_workspace(workspace_id)
            print(f"Cleaned up workspace {workspace_id}")

        except Exception as e:
            print(f"Error in advanced example: {e}")


async def error_handling_example():
    """Example showing proper error handling"""

    config = AnythingLLMConfig(
        base_url="http://invalid-url:9999",  # Invalid URL for testing
        timeout=5,
        max_retries=1,
    )

    async with AnythingLLMRepository(config) as repo:
        try:
            # This will fail due to invalid URL
            result = await repo.get("/api/v1/workspaces")
            print(f"Result: {result}")

        except NetworkError as e:
            print(f"Network error caught: {e}")
        except AuthenticationError as e:
            print(f"Authentication error caught: {e}")
        except AnythingLLMRepositoryError as e:
            print(f"Repository error caught: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def concurrent_requests_example():
    """Example showing concurrent requests"""

    config = AnythingLLMConfig(base_url="http://localhost:3001", api_key="your-api-key-here")

    async with AnythingLLMRepository(config) as repo:
        try:
            # Make multiple concurrent requests
            tasks = [repo.get("/api/v1/workspaces"), repo.get("/api/v1/system/health"), repo.get("/api/v1/system/info")]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Task {i} failed: {result}")
                else:
                    print(f"Task {i} succeeded: {result}")

        except Exception as e:
            print(f"Error in concurrent example: {e}")


async def main():
    """Main function to run all examples"""
    print("=== AnythingLLM Repository Usage Examples ===\n")

    print("1. Basic Usage Example:")
    await basic_usage_example()
    print("\n" + "=" * 50 + "\n")

    print("2. Advanced Usage Example:")
    await advanced_usage_example()
    print("\n" + "=" * 50 + "\n")

    print("3. Error Handling Example:")
    await error_handling_example()
    print("\n" + "=" * 50 + "\n")

    print("4. Concurrent Requests Example:")
    await concurrent_requests_example()
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the examples
    asyncio.run(main())
