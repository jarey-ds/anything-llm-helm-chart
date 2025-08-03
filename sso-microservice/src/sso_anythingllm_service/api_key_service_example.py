"""
Example usage of ApiKeyService.

This example demonstrates how to use the ApiKeyService for CRUD operations.
"""

import asyncio

from kink import di

from sso_anythingllm_dto.api_key import ApiKeyDto
from sso_anythingllm_repository.api_key_repository import ApiKeyRepository
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_service.api_key_service import ApiKeyService


async def main():
    """Example usage of ApiKeyService."""

    # Set up dependencies
    db_config = AsyncPostgresConf(
        host="localhost", port=5432, username="postgres", password="password", database="anythingllm"
    )

    # Register dependencies
    di[AsyncPostgresConf] = db_config
    di[ApiKeyRepository] = ApiKeyRepository(db_config)

    # Get service instance
    api_key_service = di[ApiKeyService]

    print("🔑 ApiKeyService CRUD Operations Example")
    print("=" * 50)

    # ──────────────────────────── CREATE ────────────────────────────
    print("\n1. Creating API keys...")

    api_key1 = ApiKeyDto(value="api-key-123")
    api_key2 = ApiKeyDto(value="api-key-456")

    saved_api_key1 = await api_key_service.save(api_key1)
    saved_api_key2 = await api_key_service.save(api_key2)

    print(f"✅ Created API key: {saved_api_key1.value}")
    print(f"✅ Created API key: {saved_api_key2.value}")

    # ──────────────────────────── READ ────────────────────────────
    print("\n2. Reading API keys...")

    # Get by value
    retrieved_api_key = await api_key_service.get_api_key_by_value("api-key-123")
    print(f"✅ Retrieved API key: {retrieved_api_key.value}")

    # Get all API keys
    all_api_keys = await api_key_service.get_all_api_keys()
    print(f"✅ Total API keys: {len(all_api_keys)}")
    for api_key in all_api_keys:
        print(f"   - {api_key.value}")

    # Check if exists
    exists = await api_key_service.api_key_exists("api-key-123")
    print(f"✅ API key 'api-key-123' exists: {exists}")

    # Count API keys
    count = await api_key_service.count_api_keys()
    print(f"✅ Total API keys count: {count}")

    # ──────────────────────────── UPDATE ────────────────────────────
    print("\n3. Updating API key...")

    # Update the API key (in this case, ApiKey only has one field)
    updated_api_key = await api_key_service.update(saved_api_key1)
    print(f"✅ Updated API key: {updated_api_key.value}")

    # ──────────────────────────── DELETE ────────────────────────────
    print("\n4. Deleting API key...")

    await api_key_service.delete_by_value("api-key-456")
    print("✅ Deleted API key: api-key-456")

    # Verify deletion
    remaining_keys = await api_key_service.get_all_api_keys()
    print(f"✅ Remaining API keys: {len(remaining_keys)}")
    for api_key in remaining_keys:
        print(f"   - {api_key.value}")

    # ──────────────────────────── LEGACY METHODS ────────────────────────────
    print("\n5. Using legacy methods...")

    # Legacy create
    legacy_api_key = ApiKeyDto(value="legacy-api-key")
    created_api_key = await api_key_service.create(legacy_api_key)
    print(f"✅ Created with legacy method: {created_api_key.value}")

    # Legacy get all
    legacy_keys = await api_key_service.get_api_keys()
    print(f"✅ Retrieved with legacy method: {len(legacy_keys)} keys")

    # Legacy delete
    await api_key_service.delete(created_api_key)
    print("✅ Deleted with legacy method")

    print("\n🎉 All CRUD operations completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
