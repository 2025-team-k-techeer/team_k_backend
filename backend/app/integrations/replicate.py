# 코드 어차피 작동 안됨. Refactoring 필요
# 이 코드는 Replicate API를 사용하여 이미지를 생성하고 저장하는 기능을 포함
import os
import time
import httpx
import asyncio
from typing import Optional
from app.config import get_settings

settings = get_settings()


class ReplicateService:
    """Replicate API를 사용한 이미지 생성 서비스"""

    def __init__(self):
        self.api_key = settings.REPLICATE_API_KEY
        self.base_url = "https://api.replicate.com/v1"
        self.model_version = (
            "854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b"
        )

    def _get_headers(self) -> dict:
        """API 요청 헤더 생성"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}",
        }

    def _build_prompt(self, room_type: str, style: str, prompt: str) -> str:
        """프롬프트 생성"""
        base_prompt = f"a {style.lower()} {room_type.lower()}"
        if prompt:
            base_prompt += f", {prompt}"
        return base_prompt

    async def generate_interior_image(
        self, image_url: str, room_type: str, style: str, prompt: str
    ) -> Optional[str]:
        """
        인테리어 이미지 생성

        Args:
            image_url: 원본 이미지 URL
            room_type: 방 유형 (거실, 침실, 주방 등)
            style: 스타일 (모던, 북유럽 등)
            prompt: 추가 요구사항

        Returns:
            생성된 이미지 URL 또는 None (실패 시)
        """
        try:
            # 프롬프트 생성
            generated_prompt = self._build_prompt(room_type, style, prompt)

            # API 요청 페이로드
            payload = {
                "version": self.model_version,
                "input": {
                    "image": image_url,
                    "prompt": generated_prompt,
                    "a_prompt": "best quality, extremely detailed, photo from Pinterest, interior, cinematic photo, ultra-detailed, ultra-realistic, award-winning, professional interior design",
                    "n_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, blurry, distorted, deformed",
                },
            }

            async with httpx.AsyncClient() as client:
                # 예측 생성 요청
                response = await client.post(
                    f"{self.base_url}/predictions",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()

                prediction_data = response.json()
                get_url = prediction_data["urls"]["get"]

                # 결과 폴링
                generated_image_url = await self._poll_prediction_result(
                    client, get_url
                )

                if generated_image_url:
                    print(
                        f"✅ Interior image generated successfully for {room_type} with {style} style"
                    )
                    return generated_image_url
                else:
                    print(f"❌ Failed to generate interior image for {room_type}")
                    return None

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error in Replicate API: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error in Replicate service: {str(e)}")
            return None

    async def _poll_prediction_result(
        self, client: httpx.AsyncClient, get_url: str
    ) -> Optional[str]:
        """예측 결과 폴링"""
        max_attempts = 60  # 최대 60초 대기
        attempt = 0

        while attempt < max_attempts:
            try:
                poll_response = await client.get(
                    get_url, headers=self._get_headers(), timeout=10.0
                )
                poll_response.raise_for_status()
                poll_data = poll_response.json()

                if poll_data["status"] == "succeeded":
                    # 성공 시 두 번째 이미지 반환 (일반적으로 더 나은 품질)
                    output = poll_data["output"]
                    if isinstance(output, list) and len(output) > 1:
                        return output[1]  # 두 번째 이미지
                    elif isinstance(output, list) and len(output) > 0:
                        return output[0]  # 첫 번째 이미지
                    elif isinstance(output, str):
                        return output  # 단일 이미지 URL
                    else:
                        print("❌ Unexpected output format from Replicate")
                        return None

                elif poll_data["status"] == "failed":
                    print(
                        f"❌ Prediction failed: {poll_data.get('error', 'Unknown error')}"
                    )
                    return None
                else:
                    # 진행 중이면 대기
                    print(f"⏳ Polling... Status: {poll_data['status']}")
                    await asyncio.sleep(1)
                    attempt += 1

            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP Error while polling: {e.response.text}")
                return None
            except Exception as e:
                print(f"❌ Error while polling: {str(e)}")
                return None

        print("❌ Timeout waiting for prediction result")
        return None


# 기존 함수 호환성을 위한 래퍼
async def generate_image(image_url: str, theme: str, room: str):
    """기존 함수 호환성을 위한 래퍼"""
    service = ReplicateService()
    return await service.generate_interior_image(image_url, room, theme, "")
