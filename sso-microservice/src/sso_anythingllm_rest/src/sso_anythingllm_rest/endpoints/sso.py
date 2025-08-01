"""This module contains the implementation of the SSO management-related endpoints."""

from typing import Annotated

# Source imports
# ────────────────────────────────────────── imports ────────────────────────────────────────── #
from fastapi import APIRouter, Depends, FastAPI
from fastapi.security import OAuth2
from kink import di
from pydantic import BaseModel
from starlette.status import HTTP_200_OK

from sso_anythingllm_dto.user import KeycloakUserDto
from sso_anythingllm_facade.interfaces.sso_facade_interface import SSOFacadeInterface

# ───────────────────────────────────────────────────────────────────────────────────────────── #
#                                    API Router Configuration                                   #
# ───────────────────────────────────────────────────────────────────────────────────────────── #

ROUTER_TAG = "SSO Integration"
router = APIRouter()

sso_facade: SSOFacadeInterface = di[SSOFacadeInterface]

# Create mapper instances at module level for reuse
# provider_instance_dto_to_to_mapper = ProviderInstanceDtoToProviderToMapper()


oauth2_scheme = OAuth2()


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    return User(username=token + "fakedecoded", email="john@example.com", full_name="John Doe")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


def init_app(app: FastAPI, prefix: str = "") -> str:
    """This method integrates this APIRouter into the indicated FastAPI application."""
    endpoint_prefix = prefix or "/api"
    app.include_router(
        router,
        prefix=f"{endpoint_prefix}/sso",
    )
    return endpoint_prefix


# ───────────────────────────────────────────────────────────────────────────────────────────── #
#                                  API endpoints implementation                                 #
# ───────────────────────────────────────────────────────────────────────────────────────────── #


@router.get(
    "/url",
    tags=[ROUTER_TAG],
    status_code=HTTP_200_OK,
    response_model=str,
)
async def get_sso_url(current_user: Annotated[User, Depends(get_current_user)]) -> str:
    """
    Gets the temporarily access URL to a given user on AnythingLLM.
    """
    # Extract information from the token
    user_dto: KeycloakUserDto = KeycloakUserDto(id="aloha", name="Jose", groups=["admin"])
    # Get the URL
    url = await sso_facade.get_anything_llm_sso_url(user=user_dto)

    # Provide the URL as a result
    return url
