from fastapi import APIRouter, HTTPException
from app.interior.infra.repository.ar_repository import ARRepository
from app.interior.schemas.ar_schema import (
    ARSimilarObjectRequest,
    ARObject,
    ARPosition,
    ARSimilarObjectResponse,
)

router = APIRouter(prefix="/api/ar", tags=["AR"])

ar_repository = ARRepository()


@router.post("/similar-object", response_model=ARSimilarObjectResponse)
async def get_similar_ar_objects(request: ARSimilarObjectRequest):
    label = request.label
    if not label:
        raise HTTPException(status_code=400, detail="label 정보가 누락되었습니다.")

    # 1. AR Document에서 label로 3D 모델 조회
    ar_docs = await ar_repository.get_ar_documents_by_label(label)
    if not ar_docs:
        return {
            "status": "error",
            "message": f"해당 label({label})에 대한 AR 모델 정보가 없습니다.",
            "objects": [],
        }

    # 2. danawa_products에서 label로 상품 정보 조회
    danawa_docs = await ar_repository.get_danawa_products_by_label(label)

    # 3. 상품 크기 정보 추출 (평균값 계산)
    widths = [
        d["dimensions"]["width_cm"]
        for d in danawa_docs
        if d.get("dimensions") and d["dimensions"].get("width_cm") is not None
    ]
    depths = [
        d["dimensions"]["depth_cm"]
        for d in danawa_docs
        if d.get("dimensions") and d["dimensions"].get("depth_cm") is not None
    ]
    heights = [
        d["dimensions"]["height_cm"]
        for d in danawa_docs
        if d.get("dimensions") and d["dimensions"].get("height_cm") is not None
    ]
    avg_width = sum(widths) / len(widths) if widths else None
    avg_depth = sum(depths) / len(depths) if depths else None
    avg_height = sum(heights) / len(heights) if heights else None

    # 4. AR 객체에 크기 정보 추가
    objects = []
    for d in ar_docs[:3]:  # 최대 3개 객체 반환
        objects.append(
            ARObject(
                id=str(d["_id"]),
                label=d["label"],
                model_url=d["model_url"],
                image_url=d["image_url"],
                position=ARPosition(**d["position"]),
                rotation=d["rotation"],
                scale=d["scale"],
                width=avg_width,
                depth=avg_depth,
                height=avg_height,
            )
        )

    return {
        "status": "success",
        "message": f"유사한 {label} 객체를 반환합니다.",
        "objects": objects,
    }
