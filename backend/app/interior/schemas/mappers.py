from typing import List
from app.interior.domain.interior import (
    Interior,
    FurnitureDetected,
)
from app.interior.schemas.interior_schema import (
    InteriorGenerateResponse,
    Dimensions as DimensionsSchema,
    DanawaProduct as DanawaProductSchema,
    BoundingBox as BoundingBoxSchema,
    DetectedPart,
)


def domain_to_interior_generate_response(
    interior: Interior, furnitures: List[FurnitureDetected], products_map: dict
) -> InteriorGenerateResponse:
    detected_parts_response = []
    for furniture in furnitures:
        danawa_products = []
        for pid in furniture.danawa_products_id:
            product = products_map.get(pid)
            if product:
                danawa_products.append(
                    DanawaProductSchema(
                        id=product.id,
                        name=product.product_name,
                        product_url=product.product_url,
                        image_url=product.image_url,
                        dimensions=DimensionsSchema(
                            width_cm=product.dimensions.width_cm,
                            depth_cm=product.dimensions.depth_cm,
                            height_cm=product.dimensions.height_cm,
                        ),
                    )
                )
        detected_parts_response.append(
            DetectedPart(
                id=furniture.id,
                bounding_box=BoundingBoxSchema(
                    x=furniture.bounding_box.x,
                    y=furniture.bounding_box.y,
                    width=furniture.bounding_box.width,
                    height=furniture.bounding_box.height,
                ),
                danawa_products=danawa_products,
                created_at=furniture.created_at,
            )
        )
    return InteriorGenerateResponse(
        id=interior.id,
        status="success",
        original_image_url=interior.original_image_url,
        generated_image_url=interior.generated_image_url,
        saved=interior.saved,
        detected_parts=detected_parts_response,
    )


def domain_to_user_library_interior(interior, furniture_map) -> "UserLibraryInterior":
    from app.interior.schemas.interior_schema import (
        UserLibraryInterior,
        UserLibraryDetectedPart,
        UserLibraryBoundingBox,
    )

    detected_parts = []
    for furniture_id in interior.detected_parts or []:
        furniture = furniture_map.get(furniture_id)
        if not furniture:
            continue
        detected_parts.append(
            UserLibraryDetectedPart(
                furniture_id=furniture.id,
                label=furniture.label,
                bounding_box=UserLibraryBoundingBox(
                    x=furniture.bounding_box.x,
                    y=furniture.bounding_box.y,
                    width=furniture.bounding_box.width,
                    height=furniture.bounding_box.height,
                ),
                danawa_products_id=furniture.danawa_products_id,
            )
        )
    return UserLibraryInterior(
        interior_id=interior.id,
        original_image_url=interior.original_image_url,
        generated_image_url=interior.generated_image_url,
        interior_type_id=interior.interior_type_id,
        room_type_id=interior.room_type_id,
        status=interior.status,
        created_at=interior.created_at,
        detected_parts=detected_parts,
    )


def interior_type_to_style_info_item(style: "InteriorType") -> "StyleInfo":
    from app.interior.schemas.interior_schema import StyleInfo

    return StyleInfo(
        style_id=style.id,
        name=style.name,
        description=style.description,
    )


def interior_type_to_style_info_response(style: "InteriorType") -> dict:
    from app.interior.schemas.interior_schema import StyleInfoResponse

    return StyleInfoResponse(
        status="success",
        style_id=style.id,
        name=style.name,
        description=style.description,
    )
