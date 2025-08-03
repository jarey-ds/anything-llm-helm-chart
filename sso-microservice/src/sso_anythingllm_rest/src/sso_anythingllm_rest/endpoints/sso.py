"""This module contains the implementation of the SSO management-related endpoints."""

from typing import Annotated, Dict

import jwt

# Source imports
# ────────────────────────────────────────── imports ────────────────────────────────────────── #
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2
from pydantic import BaseModel
from starlette.status import HTTP_200_OK

from sso_anythingllm_facade.interfaces.sso_facade_interface import SSOFacadeInterface
from sso_anythingllm_facade.sso_facade import NotAuthorizedException
from sso_anythingllm_rest.dependencies import LazySingleton

# ───────────────────────────────────────────────────────────────────────────────────────────── #
#                                    API Router Configuration                                   #
# ───────────────────────────────────────────────────────────────────────────────────────────── #

ROUTER_TAG = "SSO Integration"
router = APIRouter()

sso_facade = LazySingleton(SSOFacadeInterface)


oauth2_scheme = OAuth2()


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def decode_token(token):
    # Bearer token, we split the string and take the last occurence after the space
    if " " in token:
        token = token.split(" ")[1]

    decoded: dict = jwt.decode(token, options={"verify_signature": False})

    return decoded


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> Dict:
    user_dict = decode_token(token)
    return user_dict


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
async def get_sso_url(current_user: Annotated[Dict, Depends(get_current_user)]) -> str:
    """
    Gets the temporarily access URL to a given user on AnythingLLM.
    """
    # Map user's info form the token processed as a dict to a business logic model.
    # user_dto: KeycloakUserDto = KeycloakUserDto(id="aloha", name="Jose", groups=["admin"])
    # Get the URL
    try:
        # Provide the URL as a result
        return await sso_facade.get_anything_llm_sso_url(user=current_user)
    except NotAuthorizedException as error:
        raise HTTPException(status_code=403, detail=error.message)
