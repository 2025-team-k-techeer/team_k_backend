import hashlib
import os
from typing import Optional
from datetime import datetime
from google.cloud import storage
from PIL import Image
import io
from app.config import get_settings

settings = get_settings()


class GCSService:
    """Google Cloud Storage 서비스"""

    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _generate_filename(self, original_filename: str, user_id: str) -> str:
        """
        SHA256 기반으로 암호화된 파일명 생성
        """
        # 현재 시간과 사용자 ID를 조합하여 고유한 해시 생성
        timestamp = datetime.utcnow().isoformat()
        content = f"{user_id}_{timestamp}_{original_filename}"
        hash_object = hashlib.sha256(content.encode())
        return f"{hash_object.hexdigest()}.jpg"

    def _convert_to_jpg(self, image_data: bytes) -> bytes:
        """
        이미지를 JPG 형식으로 변환
        """
        try:
            # PIL을 사용하여 이미지 열기
            image = Image.open(io.BytesIO(image_data))

            # RGBA 모드인 경우 RGB로 변환 (JPG는 알파 채널을 지원하지 않음)
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")

            # JPG로 변환하여 바이트로 반환
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=95, optimize=True)
            return output.getvalue()
        except Exception as e:
            raise Exception(f"이미지 변환 실패: {str(e)}")

    async def upload_image(
        self, image_data: bytes, original_filename: str, user_id: str
    ) -> dict:
        """
        이미지를 GCS에 업로드하고 공개 URL 반환

        Args:
            image_data: 이미지 바이트 데이터
            original_filename: 원본 파일명
            user_id: 사용자 ID

        Returns:
            dict: {
                "public_url": str,
                "filename": str,
                "size": int
            }
        """
        try:
            # 이미지를 JPG로 변환
            jpg_data = self._convert_to_jpg(image_data)

            # 암호화된 파일명 생성
            filename = self._generate_filename(original_filename, user_id)

            # GCS에 업로드
            blob = self.bucket.blob(f"user/upload/{filename}")
            blob.upload_from_string(jpg_data, content_type="image/jpeg")
            blob.make_public()  # 공개 URL 생성
            if not blob.public_url:
                raise Exception("이미지 업로드 후 공개 URL 생성 실패")

            # 공개 URL 생성
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/user/upload/{filename}"

            return {
                "public_url": public_url,
                "filename": filename,
                "size": len(jpg_data),
            }

        except Exception as e:
            raise Exception(f"GCS 업로드 실패: {str(e)}")

    async def delete_image(self, filename: str) -> bool:
        """
        GCS에서 이미지 삭제

        Args:
            filename: 삭제할 파일명

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            blob = self.bucket.blob(f"user/upload/{filename}")
            blob.delete()
            return True
        except Exception as e:
            print(f"이미지 삭제 실패: {str(e)}")
            return False
