import csv
import json
import os
import uuid
from datetime import datetime, timezone
from collections import defaultdict

# 경로 설정
base_input_dir = "./data/gcs_furniture_csv/"
output_path = "./data/mongo/collections/danawa_products.json"

# 임시 저장 딕셔너리: name 기준으로 병합
product_map = defaultdict(
    lambda: {
        "_id": None,
        "label": "",
        "product_name": "",
        "product_url": "",
        "image_url": [],
        "dimensions": {},
        "created_at": "",
        "updated_at": "",
    }
)

# 파일 순회 (폴더 X)
for file in os.listdir(base_input_dir):
    if not file.endswith(".csv"):
        continue

    file_path = os.path.join(base_input_dir, file)

    # 파일명 기준 label 추출
    filename = os.path.splitext(file)[0]  # 예: desk_gcs
    label = filename.replace("_gcs", "")  # 예: desk

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row["name"]
            if name not in product_map:
                product_map[name]["_id"] = str(uuid.uuid4())
                product_map[name]["label"] = label
                product_map[name]["product_name"] = name
                product_map[name]["product_url"] = row["product_url"]
                product_map[name]["dimensions"] = {
                    "width_cm": int(float(row["width"])) if row["width"] else None,
                    "depth_cm": int(float(row["depth"])) if row["depth"] else None,
                    "height_cm": int(float(row["height"])) if row["height"] else None,
                }
                now = datetime.now(timezone.utc).isoformat() + "Z"
                product_map[name]["created_at"] = now
                product_map[name]["updated_at"] = now

            # image_url 중복 없이 추가
            image_url = row["image_url"]
            if image_url and image_url not in product_map[name]["image_url"]:
                product_map[name]["image_url"].append(image_url)


# JSON 파일로 저장
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as jsonfile:
    json.dump(list(product_map.values()), jsonfile, ensure_ascii=False, indent=2)

print(f"✅ JSON saved to {output_path} ({len(product_map)} items)")
