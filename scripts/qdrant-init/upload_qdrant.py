import os
import time
import json
import requests
from google.cloud import storage


def wait_for_qdrant(qdrant_url, timeout=60):
    print(f"[INFO] Qdrant 준비 대기 중... ({qdrant_url})")
    for _ in range(timeout):
        try:
            r = requests.get(f"{qdrant_url}/collections")
            if r.status_code == 200:
                print("[INFO] Qdrant가 준비되었습니다.")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("[ERROR] Qdrant가 준비되지 않았습니다.")
    return False


def download_from_gcs(bucket_name, blob_name, dest_path):
    print(f"[INFO] GCS에서 {bucket_name}/{blob_name} 다운로드 중...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(dest_path)
    print(f"[INFO] 다운로드 완료: {dest_path}")


def create_collection_if_not_exists(
    qdrant_url, collection, vector_size, distance="Cosine"
):
    url = f"{qdrant_url}/collections/{collection}"
    resp = requests.get(url)
    if resp.status_code == 200:
        print(f"[INFO] 컬렉션 '{collection}' 이미 존재.")
        return
    print(f"[INFO] 컬렉션 '{collection}' 생성 중...")
    data = {"vectors": {"size": vector_size, "distance": distance}}
    resp = requests.put(url, json=data)
    if resp.status_code not in (200, 201):
        print(f"[ERROR] 컬렉션 생성 실패: {resp.status_code} {resp.text}")
        exit(1)
    print(f"[INFO] 컬렉션 생성 완료.")


def parse_points(raw_points, vector_size=768):
    points = []
    skipped = 0
    for idx, item in enumerate(raw_points):
        vec = item.get("vector")
        if vec is None or len(vec) != vector_size:
            print(
                f"[SKIP] {idx}번째 포인트: 벡터 길이 불일치({len(vec) if vec else 'None'})"
            )
            skipped += 1
            continue
        payload = item.get("payload", {})
        point = {
            "id": idx,  # 항상 순번으로 id 지정 (중복 방지)
            "vector": vec,
            "payload": payload,
        }
        points.append(point)
    print(f"[INFO] 총 {skipped}개 포인트가 업로드에서 제외됨")
    return points


def upload_to_qdrant(qdrant_url, collection, points):
    url = f"{qdrant_url}/collections/{collection}/points"
    headers = {"Content-Type": "application/json"}
    batch_size = 100
    total_uploaded = 0
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        data = {"points": batch}
        resp = requests.put(url, headers=headers, data=json.dumps(data))
        print(f"[Qdrant 응답] {resp.status_code} {resp.text}")
        if resp.status_code not in (200, 201):
            print(f"[ERROR] 업로드 실패: {resp.status_code} {resp.text}")
        else:
            print(f"[INFO] {i+1}~{i+len(batch)} 포인트 업로드 성공")
            total_uploaded += len(batch)
    print(f"[INFO] 총 업로드 시도 포인트 수: {len(points)}")
    print(f"[INFO] 업로드 성공 포인트 수: {total_uploaded}")
    return total_uploaded


def check_qdrant_points_count(qdrant_url, collection):
    url = f"{qdrant_url}/collections/{collection}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            info = resp.json()
            count = info["result"].get("points_count", None)
            print(f"[INFO] Qdrant 컬렉션 '{collection}'의 현재 포인트 개수: {count}")
            return count
        else:
            print(
                f"[ERROR] Qdrant 컬렉션 정보 조회 실패: {resp.status_code} {resp.text}"
            )
            return None
    except Exception as e:
        print(f"[ERROR] Qdrant 포인트 개수 확인 중 예외 발생: {e}")
        return None


def main():
    GCS_BUCKET = os.environ["GCS_BUCKET"]
    GCS_BLOB = os.environ["GCS_QDRANT_EMBEDDINGS_JSON"]
    QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
    QDRANT_COLLECTION = os.environ["QDRANT_COLLECTION"]
    VECTOR_SIZE = int(os.environ.get("QDRANT_VECTOR_SIZE", "384"))  # 벡터 크기(예시)
    QDRANT_DISTANCE = os.environ.get("QDRANT_DISTANCE", "Cosine")
    LOCAL_PATH = "/tmp/furniture_embeddings.json"

    if not wait_for_qdrant(QDRANT_URL):
        exit(1)

    download_from_gcs(GCS_BUCKET, GCS_BLOB, LOCAL_PATH)

    with open(LOCAL_PATH, "r", encoding="utf-8") as f:
        raw_points = json.load(f)
    points = parse_points(raw_points)

    create_collection_if_not_exists(
        QDRANT_URL, QDRANT_COLLECTION, VECTOR_SIZE, QDRANT_DISTANCE
    )

    uploaded = upload_to_qdrant(QDRANT_URL, QDRANT_COLLECTION, points)

    # 업로드 후 실제 Qdrant에 저장된 포인트 개수 확인
    print("[INFO] 데이터 반영 대기 중...")
    time.sleep(20)
    count = check_qdrant_points_count(QDRANT_URL, QDRANT_COLLECTION)
    if count is not None:
        if count >= uploaded:
            print(
                f"[SUCCESS] Qdrant에 데이터가 정상적으로 업로드되었습니다! (총 {count}개)"
            )
        else:
            print(
                f"[WARNING] 업로드 시도({uploaded}) 대비 실제 저장({count}) 개수가 다릅니다. 일부 실패 가능성 있음."
            )
    else:
        print(
            "[ERROR] Qdrant 포인트 개수 확인 실패. 업로드 결과를 수동으로 확인하세요."
        )

    print("[INFO] 모든 작업이 완료되었습니다.")


if __name__ == "__main__":
    main()
