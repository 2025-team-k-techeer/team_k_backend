from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.interior.application.interior_service import InteriorService
from app.interior.schemas.interior_schema import (
    InteriorTypeQuery,
    InteriorTypeResponse,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt_utils import (
    get_current_user_id,
)

router = APIRouter(prefix="/interiors", tags=["Interior API"])

interior_service = InteriorService()
security = HTTPBearer()


# TODO: async or sync?
@router.get("/styles")
async def get_interior_item(
    query: Annotated[InteriorTypeQuery, Query()],
    token: HTTPAuthorizationCredentials = Depends(security),
):
    """
    제공된 검색 기준에 따라 내부 가구 스타일을 검색합니다.

    Args:
        search_body (FurnitureTypeQuery): 스타일 이름을 포함한 검색 기준으로 가구 스타일을 필터링합니다.

    Returns:
        InteriorTypeResponse: 내부 스타일 검색 결과를 포함하는 검증된 응답 객체입니다.
    """
    if token.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
        )
    _ = get_current_user_id(token.credentials)

    result = await interior_service.search_interior(query.name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interior style '{query.name}' not found.",
        )

    return {"description": result.get("description", "")}
