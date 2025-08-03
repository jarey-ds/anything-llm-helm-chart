"""
Example usage of UserRepository for CRUD operations on User entities.

This example demonstrates how to:
1. Create a new user
2. Retrieve a user by Keycloak ID
3. Update user information
4. Delete a user
5. List all users
6. Filter users by role
"""

import asyncio

from sso_anythingllm_entity.user import User
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError
from sso_anythingllm_repository.user_repository import UserRepository


async def main():
    """Main example function demonstrating UserRepository usage."""

    # Initialize database configuration
    db_config = AsyncPostgresConf(
        username="sso-anythingllm",
        password="sso-anythingllm123",
        database="sso_anythingllm",
        host="localhost",
        port=5432,
    )

    # Create repository instance
    user_repository = UserRepository(db_config)

    try:
        # Example 1: Create a new user
        print("=== Creating a new user ===")
        new_user = User(keycloak_id="user-123", internal_id=1, name="John Doe", role="admin")

        created_user = await user_repository.save(new_user)
        print(f"Created user: {created_user.name} with role {created_user.role}")

        # Example 2: Retrieve user by Keycloak ID
        print("\n=== Retrieving user by Keycloak ID ===")
        retrieved_user = await user_repository.get_by_keycloak_id("user-123")
        print(f"Retrieved user: {retrieved_user.name}")

        # Example 3: Update user information
        print("\n=== Updating user information ===")
        updated_user = User(
            keycloak_id="user-123",
            internal_id=1,
            name="John Smith",  # Changed name
            role="manager",  # Changed role
        )

        result = await user_repository.update(updated_user)
        print(f"Updated user: {result.name} with new role {result.role}")

        # Example 4: Create more users for demonstration
        print("\n=== Creating additional users ===")
        users_to_create = [
            User(keycloak_id="user-456", internal_id=2, name="Jane Doe", role="default"),
            User(keycloak_id="user-789", internal_id=3, name="Bob Wilson", role="manager"),
            User(keycloak_id="user-101", internal_id=4, name="Alice Brown", role="admin"),
        ]

        for user in users_to_create:
            await user_repository.save(user)
            print(f"Created user: {user.name}")

        # Example 5: List all users
        print("\n=== Listing all users ===")
        all_users = await user_repository.get_all_users()
        print(f"Total users: {len(all_users)}")
        for user in all_users:
            print(f"- {user.name} ({user.role})")

        # Example 6: Filter users by role
        print("\n=== Filtering users by role ===")
        admin_users = await user_repository.get_users_by_role("admin")
        print(f"Admin users: {len(admin_users)}")
        for user in admin_users:
            print(f"- {user.name}")

        manager_users = await user_repository.get_users_by_role("manager")
        print(f"Manager users: {len(manager_users)}")
        for user in manager_users:
            print(f"- {user.name}")

        # Example 7: Check if user exists
        print("\n=== Checking user existence ===")
        exists = await user_repository.user_exists("user-123")
        print(f"User user-123 exists: {exists}")

        not_exists = await user_repository.user_exists("non-existent-user")
        print(f"User non-existent-user exists: {not_exists}")

        # Example 8: Count total users
        print("\n=== Counting users ===")
        total_count = await user_repository.count_users()
        print(f"Total users in database: {total_count}")

        # Example 9: Delete a user
        print("\n=== Deleting a user ===")
        await user_repository.delete_by_keycloak_id("user-456")
        print("Deleted user with keycloak_id: user-456")

        # Verify deletion
        final_count = await user_repository.count_users()
        print(f"Users after deletion: {final_count}")

    except ValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
