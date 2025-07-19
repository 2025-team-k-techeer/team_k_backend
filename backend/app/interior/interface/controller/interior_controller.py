from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from app.interior.application.interior_service import InteriorService
from backend.app.interior.schemas.interior_schema import (
    InteriorTypeQuery,
    InteriorTypeResponse,
)

router = APIRouter(prefix="/interiors", tags=["Interior API"])

interior_service = InteriorService()


# TODO: async or sync?
@router.get("/styles")
async def get_interior_items(query: Annotated[InteriorTypeQuery, Query()]):
    """
    Handles the retrieval of interior furniture styles based on the provided search criteria.

    Args:
        search_body (FurnitureTypeQuery): The search criteria containing the style name to filter furniture styles.

    Returns:
        FurnitureStyleResponse: A validated response object containing the search results for furniture styles.
    """
    result = await interior_service.search_furniture(query.name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Furniture style '{query.name}' not found.",
        )
    response = InteriorTypeResponse(
        _id=result["_id"],
        description=result["description"],
        name=result["name"],
        example_image_url=result["example_image_url"],
    )
    return response
