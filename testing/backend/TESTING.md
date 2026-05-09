# Backend Testing Guide

เอกสารนี้ครอบคลุมการทดสอบ backend ด้วย 3 แบบ:
- Unit test: ทดสอบ business logic แยกส่วนด้วย mock
- Integration test: ทดสอบ API route + request/response contract
- Manual/API collection: ใช้ Postman และ Robot Framework สำหรับ smoke test

## 1) เป้าหมายรอบแรก
- โฟกัส backend ก่อน
- เน้น critical path ของ user message/conversation flow
- รองรับการทำงานร่วมกับ RLS โดยส่ง `Authorization` token ผ่าน API

## 2) Test Scope
- Unit: `services/services_conversation.py`
- Integration: router layer และ helper ของ backend หลัก
- ครอบคลุมกรณีสำคัญ:
  - conversation rooms และ messages
  - users profile CRUD และ options endpoints
  - acts / sections / libraries / judgments / help / utility routes
  - chat sync และ chat stream

## 2.1) Test Case Matrix
ถ้าต้องการดูรายการ test case แบบ `Test Case / Act / Expected / Actual` ให้เปิด:
- `TEST_CASES.md` (สรุป 1 หน้า)
- `TEST_CASES_APPENDIX.md` (ภาคผนวกฉบับละเอียด)

## 3) ติดตั้งเครื่องมือทดสอบ
จากโฟลเดอร์ `backend`:

```powershell
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## 4) วิธีรัน Unit + Integration
จากโฟลเดอร์ `backend`:

```powershell
python -m pytest
```

รันแยกเฉพาะไฟล์:

```powershell
python -m pytest tests/test_services_conversation.py
python -m pytest tests/test_routers_conversation.py
```

Troubleshooting สั้นๆ:
- ถ้าเจอ `ModuleNotFoundError: No module named 'routers'` หรือ `'services'` ให้รันจากโฟลเดอร์ `backend` และใช้ `python -m pytest`
- ถ้าเจอ `pytest is not recognized` ให้ activate virtualenv ก่อน หรือเรียกผ่าน `python -m pytest` แทน

## 5) วิธีคิดเรื่องข้อ 5-7 (อธิบายแบบง่าย)
- ข้อ 5: CI/CD คือให้ระบบรันทดสอบอัตโนมัติทุกครั้งที่ push หรือเปิด PR
- ข้อ 6: Business rules คือกฎที่ระบบต้องทำถูกเสมอ (เช่นสิทธิ์เข้าถึงข้อมูลตาม RLS)
- ข้อ 7: Integration data คือข้อมูลทดสอบมาตรฐาน (fixture/seed) และ token สำหรับทดสอบ role ต่างๆ

เริ่มต้นได้โดยยังไม่ต้องทำข้อ 5-7 เต็มรูปแบบ แต่ควรเตรียม:
- test user token อย่างน้อย 1 ชุด
- test room/message ตัวอย่าง
- รายการ endpoint ที่ถือว่า critical

## 6) Postman
ใช้ไฟล์ collection ตัวอย่าง:
- `../testing/api/postman/ThaiLabourBackend.postman_collection.json`

การใช้งาน:
1. Import collection เข้า Postman
2. ตั้ง environment variable:
   - `baseUrl` เช่น `http://127.0.0.1:8000`
   - `token` เช่น JWT ของผู้ใช้ทดสอบ
3. รัน request ตามลำดับเพื่อทดสอบ conversation flow

## 7) Robot Framework
ไฟล์ตัวอย่าง:
- `../testing/api/robot/conversation_api.robot`
- `../testing/ui/robot/e2e_user_journey_ui.robot`

รัน:

```powershell
robot ../testing/api/robot/conversation_api.robot
robot ../testing/ui/robot/e2e_user_journey_ui.robot
```

รัน UI flow แบบ end-to-end (register/login/chat/library/history/profile/logout):

```powershell
robot \
  -V ../testing/ui/robot/e2e_user_journey_ui.variables.example.robot \
  ../testing/ui/robot/e2e_user_journey_ui.robot
```

หรือส่งตัวแปรตรงจาก command line:

```powershell
robot \
  -v FRONTEND_URL:http://localhost:3000 \
  -v BROWSER:Chrome \
  -v RUN_REGISTER:False \
  -v TEST_EMAIL:your-existing-user@example.com \
  -v TEST_PASSWORD:YourPassword123! \
  ../testing/ui/robot/e2e_user_journey_ui.robot
```

หมายเหตุ:
- Robot test จะยิง API จริง จึงต้องเปิด backend ไว้ก่อน
- หากใช้ RLS ให้ตั้งตัวแปร `${TOKEN}` เป็น token ผู้ใช้ทดสอบ
- สำหรับ `e2e_user_journey_ui.robot` ให้เปิดทั้ง backend และ frontend ก่อนรัน
- ถ้าตั้งค่า Supabase ให้ยืนยันอีเมลก่อน login ให้ใช้ `RUN_REGISTER=False` และใส่บัญชีทดสอบที่ยืนยันแล้ว
