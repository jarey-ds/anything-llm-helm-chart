import logging

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing_extensions import override

from sso_anythingllm_entity.user import User
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError
from sso_anythingllm_repository.interfaces.user_repository_interface import UserRepositoryInterface


@inject(alias=UserRepositoryInterface)
class UserRepository(UserRepositoryInterface):
    """Repository in charge of the User entity."""

    def __init__(self, db_config: AsyncPostgresConf):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def _get_session(self) -> AsyncSession:
        """Get an async database session."""
        return AsyncSession(self.db_config.engine)

    @override
    async def get_by_keycloak_id(self, keycloak_id: str) -> User:
        """Get a user by their Keycloak ID."""
        async with self._get_session() as session:
            try:
                statement = select(User).where(User.keycloak_id == keycloak_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValidationError(f"User with keycloak_id '{keycloak_id}' not found")

                return user
            except Exception as e:
                self.logger.error(f"Error retrieving user by keycloak_id '{keycloak_id}': {e}")
                raise ValidationError(f"Failed to retrieve user: {str(e)}")

    @override
    async def get_by_anythingllm_id(self, anythingllm_id: int) -> User:
        """Get a user by their AnythingLLM internal ID."""
        async with self._get_session() as session:
            try:
                statement = select(User).where(User.internal_id == anythingllm_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValidationError(f"User with internal_id '{anythingllm_id}' not found")

                return user
            except Exception as e:
                self.logger.error(f"Error retrieving user by internal_id '{anythingllm_id}': {e}")
                raise ValidationError(f"Failed to retrieve user: {str(e)}")

    # ──────────────────────────── CREATE ────────────────────────────
    @override
    async def save(self, user: User) -> User:
        """Save a new user to the database."""
        async with self._get_session() as session:
            try:
                # Check if user already exists
                if user.keycloak_id:
                    statement = select(User).where(User.keycloak_id == user.keycloak_id)
                    result = await session.execute(statement)
                    existing_user = result.scalar_one_or_none()
                    if existing_user:
                        raise ValidationError(f"User with keycloak_id '{user.keycloak_id}' already exists")

                session.add(user)
                await session.commit()
                await session.refresh(user)

                self.logger.info(f"Successfully created user with keycloak_id '{user.keycloak_id}'")
                return user
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error creating user: {e}")
                raise ValidationError(f"Failed to create user: {str(e)}")

    # ──────────────────────────── UPDATE ────────────────────────────
    @override
    async def update(self, user: User) -> User:
        """Update an existing user in the database."""
        async with self._get_session() as session:
            try:
                # Check if user exists and get the existing user
                statement = select(User).where(User.keycloak_id == user.keycloak_id)
                result = await session.execute(statement)
                db_user = result.scalar_one_or_none()

                if not db_user:
                    raise ValidationError(f"User with keycloak_id '{user.keycloak_id}' not found")

                # Update fields
                db_user.name = user.name
                db_user.role = user.role
                db_user.internal_id = user.internal_id

                await session.commit()
                await session.refresh(db_user)

                self.logger.info(f"Successfully updated user with keycloak_id '{user.keycloak_id}'")
                return db_user
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error updating user: {e}")
                raise ValidationError(f"Failed to update user: {str(e)}")

    # ──────────────────────────── DELETE ────────────────────────────
    @override
    async def delete_by_keycloak_id(self, keycloak_id: str) -> None:
        """Delete a user by their Keycloak ID."""
        async with self._get_session() as session:
            try:
                # Check if user exists and get the user to delete
                statement = select(User).where(User.keycloak_id == keycloak_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValidationError(f"User with keycloak_id '{keycloak_id}' not found")

                await session.delete(user)
                await session.commit()

                self.logger.info(f"Successfully deleted user with keycloak_id '{keycloak_id}'")
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error deleting user: {e}")
                raise ValidationError(f"Failed to delete user: {str(e)}")

    # ──────────────────────────── ADDITIONAL CRUD OPERATIONS ────────────────────────────
    async def get_all_users(self) -> list[User]:
        """Get all users from the database."""
        async with self._get_session() as session:
            try:
                statement = select(User)
                result = await session.execute(statement)
                return list(result.scalars().all())
            except Exception as e:
                self.logger.error(f"Error retrieving all users: {e}")
                raise ValidationError(f"Failed to retrieve users: {str(e)}")

    async def get_users_by_role(self, role: str) -> list[User]:
        """Get all users with a specific role."""
        async with self._get_session() as session:
            try:
                statement = select(User).where(User.role == role)
                result = await session.execute(statement)
                return list(result.scalars().all())
            except Exception as e:
                self.logger.error(f"Error retrieving users by role '{role}': {e}")
                raise ValidationError(f"Failed to retrieve users by role: {str(e)}")

    async def user_exists(self, keycloak_id: str) -> bool:
        """Check if a user exists by their Keycloak ID."""
        try:
            await self.get_by_keycloak_id(keycloak_id)
            return True
        except ValidationError:
            return False

    async def count_users(self) -> int:
        """Get the total number of users in the database."""
        async with self._get_session() as session:
            try:
                statement = select(User)
                result = await session.execute(statement)
                return len(result.scalars().all())
            except Exception as e:
                self.logger.error(f"Error counting users: {e}")
                raise ValidationError(f"Failed to count users: {str(e)}")
