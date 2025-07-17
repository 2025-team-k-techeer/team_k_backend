// init script , Docker로 MongoDB 컨테이너 시작 시 자동 초기화 (선택)
db = db.getSiblingDB("interior_db"); // 사용할 DB 이름

db.interior_type.insertMany(require("/data/interior_types.json"));