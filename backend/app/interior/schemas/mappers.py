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
    interior: Interior,
    furnitures: List[FurnitureDetected],
) -> InteriorGenerateResponse:
    detected_parts_response = []
    for furniture in furnitures:
        detected_parts_response.append(
            DetectedPart(
                id=furniture.id,
                bounding_box=BoundingBoxSchema(
                    x=furniture.bounding_box.x,
                    y=furniture.bounding_box.y,
                    width=furniture.bounding_box.width,
                    height=furniture.bounding_box.height,
                ),
                danawa_products=[
                    DanawaProductSchema(
                        id=product.id,
                        name=product.product_name,  # name 필드에 product_name 매핑
                        product_url=product.product_url,
                        image_url=product.image_url,
                        label=product.label,
                        dimensions=(
                            DimensionsSchema(
                                width_cm=(
                                    product.dimensions.width_cm
                                    if product.dimensions.width_cm is not None
                                    else 0
                                ),
                                depth_cm=(
                                    product.dimensions.depth_cm
                                    if product.dimensions.depth_cm is not None
                                    else 0
                                ),
                                height_cm=(
                                    product.dimensions.height_cm
                                    if product.dimensions.height_cm is not None
                                    else 0
                                ),
                            )
                        ),
                        created_at=product.created_at,
                        updated_at=product.updated_at,
                    )
                    for product in (furniture.danawa_products or [])
                ],
                created_at=furniture.created_at,
                label=furniture.label,
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


def domain_to_user_library_interior(
    interior, furniture_map, products_map
) -> "UserLibraryInterior":
    from app.interior.schemas.interior_schema import (
        UserLibraryInterior,
        UserLibraryDetectedPart,
        UserLibraryBoundingBox,
        DanawaProduct as DanawaProductSchema,
    )

    detected_parts = []
    for furniture_id in interior.detected_parts or []:
        furniture = furniture_map.get(furniture_id)
        if not furniture:
            continue
        danawa_products = []
        for idx, pid in enumerate(furniture.danawa_products_id or []):
            product = products_map.get(pid)
            if product:
                # 인덱스 기반으로 정확히 하나의 이미지 string만 반환
                image_url = product.image_url
                if (
                    hasattr(furniture, "danawa_products_image_index")
                    and furniture.danawa_products_image_index
                ):
                    img_idx = (
                        furniture.danawa_products_image_index[idx]
                        if idx < len(furniture.danawa_products_image_index)
                        else 0
                    )
                    if isinstance(product.image_url, list):
                        if len(product.image_url) > img_idx:
                            image_url = product.image_url[img_idx]
                        elif product.image_url:
                            image_url = product.image_url[0]
                        else:
                            image_url = ""
                # 리스트가 남아있을 가능성 방어
                if isinstance(image_url, list):
                    image_url = image_url[0] if image_url else ""
                danawa_products.append(
                    DanawaProductSchema(
                        id=product.id,
                        name=product.product_name,
                        product_url=product.product_url,
                        image_url=image_url,
                        label=product.label,
                        dimensions={
                            "width_cm": (
                                product.dimensions.width_cm
                                if product.dimensions.width_cm is not None
                                else 0
                            ),
                            "depth_cm": (
                                product.dimensions.depth_cm
                                if product.dimensions.depth_cm is not None
                                else 0
                            ),
                            "height_cm": (
                                product.dimensions.height_cm
                                if product.dimensions.height_cm is not None
                                else 0
                            ),
                        },
                    )
                )
        detected_parts.append(
            UserLibraryDetectedPart(
                furniture_id=furniture.id,
                label=furniture.label,
                bounding_box=UserLibraryBoundingBox(
                    x=float(furniture.bounding_box.x),
                    y=float(furniture.bounding_box.y),
                    width=float(furniture.bounding_box.width),
                    height=float(furniture.bounding_box.height),
                ),
                danawa_products=danawa_products,
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
    from app.config import get_settings

    settings = get_settings()

    # 기본 URL과 상대 경로를 조합하여 완전한 이미지 URL 생성
    full_image_url = None
    if style.image_url:
        # 상대 경로가 /로 시작하면 기본 URL과 조합
        if style.image_url.startswith("/"):
            full_image_url = settings.INTERIOR_STYLE_IMAGE_BASE_URL + style.image_url
        else:
            full_image_url = style.image_url

    return StyleInfo(
        style_id=style.id,
        name=style.name,
        description=style.description,
        image_url=full_image_url,
    )


def interior_type_to_style_info_response(style: "InteriorType") -> dict:
    from app.interior.schemas.interior_schema import StyleInfoResponse
    from app.config import get_settings

    settings = get_settings()

    # 기본 URL과 상대 경로를 조합하여 완전한 이미지 URL 생성
    full_image_url = None
    if style.image_url:
        # 상대 경로가 /로 시작하면 기본 URL과 조합
        if style.image_url.startswith("/"):
            full_image_url = settings.INTERIOR_STYLE_IMAGE_BASE_URL + style.image_url
        else:
            full_image_url = style.image_url

    return StyleInfoResponse(
        status="success",
        style_id=style.id,
        name=style.name,
        description=style.description,
        image_url=full_image_url,
    )
