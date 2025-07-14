import os

# main.py
if os.getenv("DEBUG", "false").lower() == "true":
    import debugpy

    try:
        debugpy.listen(("0.0.0.0", 5678))
        print("✅ VSCode 디버거 대기 중 (5678 포트)...")
        # debugpy.wait_for_client()  # 필요시
    except RuntimeError as e:
        if "Address already in use" in str(e):
            print("⚠️ debugpy 포트 5678 이미 사용 중. 중복 listen 시도 무시.")
        else:
            raise


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    print("hello")
    return {"message": "Hello World"}
