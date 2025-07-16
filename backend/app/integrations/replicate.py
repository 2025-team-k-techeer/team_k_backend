# 코드 어차피 작동 안됨. Refactoring 필요
# 이 코드는 Replicate API를 사용하여 이미지를 생성하고 저장하는 기능을 포함
import os
import time
import httpx
from collections import defaultdict
import asyncio
from urllib.parse import urlparse

# from PIL import Image
from io import BytesIO

from config import get_settings


# 환경 변수 로드
REPLICATE_API_KEY = get_settings().replicate_api_key

# 이미지 저장 폴더
IMAGE_DIR = "generated_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# 간단한 IP Rate Limiter
request_log = defaultdict(list)
RATE_LIMIT = 5
WINDOW_SECONDS = 86400
user_ip = "192.168.0.1"


def is_rate_limited(ip: str):
    now = time.time()
    request_log[ip] = [t for t in request_log[ip] if now - t < WINDOW_SECONDS]
    if len(request_log[ip]) >= RATE_LIMIT:
        return True
    request_log[ip].append(now)
    return False


def download_image_from_url(url: str, index: int):
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        # img = Image.open(BytesIO(response.content))
        # filename = f"generated_{index+1}.png"
        # filepath = os.path.join(IMAGE_DIR, filename)
        # img.save(filepath)
        # print(f"🖼️ 이미지 저장 완료: {filepath}")

        return BytesIO(response.content).getvalue()
    except Exception as e:
        print(f"⚠️ 이미지 저장 실패: {e}")
        return ""


async def generate_image(image_url: str, theme: str, room: str):
    if is_rate_limited(user_ip):
        print(":x: Too many uploads. Please try again in 24 hours.")
        return None

    prompt = (
        "a room for gaming with gaming computers, gaming consoles, and gaming chairs"
        if room.lower() == "gaming room"
        else f"a {theme.lower()} {room.lower()}"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {REPLICATE_API_KEY}",
    }

    payload = {
        "version": "854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b",
        "input": {
            "image": image_url,
            "prompt": prompt,
            "a_prompt": "best quality, extremely detailed, photo from Pinterest, interior, cinematic photo, ultra-detailed, ultra-realistic, award-winning",
            "n_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",
        },
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload,
            )
            res.raise_for_status()
            get_url = res.json()["urls"]["get"]

            restored_images = []
            while True:
                poll_res = await client.get(get_url, headers=headers)
                poll_data = poll_res.json()

                if poll_data["status"] == "succeeded":
                    restored_images = poll_data["output"]
                    break
                elif poll_data["status"] == "failed":
                    print(":x: Image generation failed.")
                    return None
                else:
                    print("⏳ Polling...")
                    await asyncio.sleep(1)

            print("✅ Image generated successfully:")
            print(restored_images)

            saved_images = []
            for i, url in enumerate(restored_images):
                img = download_image_from_url(url, i)
                if img:
                    saved_images.append(img)

            return saved_images

        except httpx.HTTPStatusError as e:
            print(":x: HTTP Error:", e.response.text)
        except Exception as e:
            print(":x: Error:", str(e))


# 단독 실행 시 테스트용
# if __name__ == "__main__":
#     test_image_url = (
#         "https://img.freepik.com/free-photo/bedroom-interior_1098-15128.jpg"
#     )
#     test_theme = "Professional black and gold"  # 테마 예시
#     test_room = "bed room"  # 방 타입 비움
#     asyncio.run(generate_image(test_image_url, test_theme, test_room))
