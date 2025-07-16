# 코드 어차피 작동 안됨. Refactoring 필요
# 이 코드는 Replicate API를 사용하여 이미지를 생성하고 저장하는 기능을 포함
import os
import time
import httpx
from collections import defaultdict
import asyncio
from PIL import Image
from io import BytesIO

from config import get_settings


def is_rate_limited(
    ip: str, api_key: str, window_seconds: int, rate_limit: int
) -> bool:
    request_log = defaultdict(list)
    now = time.time()
    request_log[ip] = [t for t in request_log[ip] if now - t < window_seconds]
    if len(request_log[ip]) >= rate_limit:
        return True
    request_log[ip].append(now)
    return False


def download_image_from_url(url: str, index: int, image_dir: str) -> str:
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        filename = f"generated_{index+1}.png"
        filepath = os.path.join(image_dir, filename)
        img.save(filepath)
        print(f"🖼️ 이미지 저장 완료: {filepath}")
        return filepath
    except Exception as e:
        print(f"⚠️ 이미지 저장 실패: {e}")
        return ""


async def generate_image(
    image_url: str,
    api_key: str,
    rate_limit: int,
    theme: str,
    room: str,
    user_ip: str,
    img_dir: str,
    window_seconds: int,
):
    if is_rate_limited(user_ip, api_key, window_seconds, rate_limit):
        print(":x: Too many uploads. Please try again in 24 hours.")
        return None

    prompt = (
        "a room for gaming with gaming computers, gaming consoles, and gaming chairs"
        if room.lower() == "gaming room"
        else f"a {theme.lower()} {room.lower()}"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {api_key}",
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

            saved_paths = []
            for i, url in enumerate(restored_images):
                path = download_image_from_url(url, i, img_dir)
                if path:
                    saved_paths.append(path)

            return saved_paths

        except httpx.HTTPStatusError as e:
            print(":x: HTTP Error:", e.response.text)
        except Exception as e:
            print(":x: Error:", str(e))
