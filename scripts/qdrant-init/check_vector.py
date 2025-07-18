import json

# vertor 길이 확인용 스크립트
# Qdrant에 업로드할 벡터의 길이를 확인하고, 일치하지 않는 벡터를 출력합니다.
# 벡터 길이가 768이 아닌 경우 경고 메시지를 출력합니다.


# 파일 경로를 실제 파일 위치로 바꿔주세요.
json_path = "data/qdrant/collections/furniture_embeddings.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

length_count = {}
for idx, item in enumerate(data):
    vec = item.get("vector")
    if vec is not None:
        l = len(vec)
        length_count[l] = length_count.get(l, 0) + 1
        if l != 768:  # Qdrant 컬렉션의 size와 다르면 샘플 출력
            print(f"[WARN] {idx}번째 포인트의 벡터 길이: {l}")
    else:
        print(f"[ERROR] {idx}번째 포인트에 'vector' 필드가 없습니다.")

print(f"총 포인트 수: {len(data)}")
print("벡터 길이별 개수:", length_count)
