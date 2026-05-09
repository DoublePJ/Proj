# Backend Test Case Matrix (Appendix - Detailed)

เอกสารภาคผนวกฉบับละเอียดนี้เก็บรายการ test case ครบทุก endpoint สำหรับอ้างอิงเชิงลึก

| ID | Module | Endpoint | Test Case | Act | Expected | Actual | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UT-01 | utility | GET / | Root welcome message | เรียก root endpoint | 200 และข้อความต้อนรับ | Passed in pytest; returned {message: Welcome to the Thai Labour Law API} | PASS |
| UT-02 | utility | GET /health | Health check | เรียก health endpoint | 200 และสถานะ ok | Passed in pytest; returned {status: ok} | PASS |
| UT-03 | utility | GET /warmup | Warmup heavy resources | เรียก warmup endpoint | 200 และโหลด resource สำเร็จ | Passed in pytest; returned {status: warmed up, message: Heavy resources loaded successfully} | PASS |
| UT-04 | utility | GET /enable-llm-router | Enable LLM router | เรียก enable-llm-router endpoint | 200 และยืนยันว่าเปิด router แล้ว | Passed in pytest; returned {status: LLM router enabled} | PASS |
| HELP-01 | help | GET /help/ | Help overview | เรียก help root | 200 และ endpoint map ระดับบน | Passed in pytest; returned top-level endpoint map | PASS |
| HELP-02 | help | GET /help/api | API groups overview | เรียก help api | 200 และกลุ่ม /api | Passed in pytest; returned api groups | PASS |
| HELP-03 | help | GET /help/api/sections | Sections help | เรียก help sections | 200 และรายการ sections endpoint | Passed in pytest; returned sections endpoint map | PASS |
| HELP-04 | help | GET /help/api/acts | Acts help | เรียก help acts | 200 และรายการ acts endpoint | Passed in pytest; returned acts endpoint map | PASS |
| HELP-05 | help | GET /help/api/libraries | Libraries help | เรียก help libraries | 200 และรายการ libraries endpoint | Passed in pytest; returned libraries endpoint map | PASS |
| HELP-06 | help | GET /help/api/conversations | Conversations help | เรียก help conversations | 200 และรายการ conversation endpoint | Passed in pytest; returned conversation endpoint map | PASS |
| HELP-07 | help | GET /help/api/users | Users help | เรียก help users | 200 และรายการ user endpoint | Passed in pytest; returned user endpoint map | PASS |
| HELP-08 | help | GET /help/llm | LLM help | เรียก help llm | 200 และรายการ llm endpoint | Passed in pytest; returned llm endpoint map | PASS |
| JUDG-01 | judgments | GET /api/judgments | Get all judgments | เรียก judgments list | 200 และรายการ judgments | Passed in pytest; returned judgment list | PASS |
| JUDG-02 | judgments | GET /api/judgments/{judgment_id} | Get judgment by id | เรียก judgment by id | 200 และ judgment object | Passed in pytest; returned judgment object | PASS |
| JUDG-03 | judgments | GET /api/judgments/{judgment_id} | Judgment not found | เรียก id ที่ไม่มีอยู่ | 404 | Passed in pytest; returned {detail: Judgment not found} | PASS |
| ACT-01 | acts | GET /api/acts/by/act_id/{act_id} | Get act by id | เรียก act by id | 200 และ act payload | Passed in pytest; returned act payload with tags and key | PASS |
| ACT-02 | acts | GET /api/acts/ | Get all acts | เรียก list acts | 200 และรายการ acts | Passed in pytest; returned act list | PASS |
| ACT-03 | acts | GET /api/acts/by/act_name/{act_name} | Get act by name | เรียก act by name | 200 และ act list หรือ 404 ถ้าไม่พบ | Covered by pytest; returned matching act payload | PASS |
| ACT-04 | acts | GET /api/acts/search/{keyword} | Search acts | เรียก search acts | 200 และรายการที่ match keyword | Passed in pytest; returned [{id: 2, title: Act Search}] | PASS |
| ACT-05 | acts | GET /api/acts/books/by/act_id/{act_id} | Get books by act id | เรียก books by act | 200 และ list of books | Passed in pytest; returned book list for act_id 10 | PASS |
| ACT-06 | acts | GET /api/acts/books/by/book_id/{book_id} | Get book by id | เรียก book by id | 200 และ book object | Covered by pytest; returned book payload | PASS |
| ACT-07 | acts | GET /api/acts/books/by/act_id/{act_id}/book_number/{book_number} | Get book by act id and number | เรียก book by act id + book number | 200 และ book object | Covered by pytest; returned matching book payload | PASS |
| ACT-08 | acts | GET /api/acts/books/search/{keyword} | Search books | เรียก search books | 200 และรายการ books ที่ match | Passed in pytest; returned [{id: 12, title: Book Search}] | PASS |
| ACT-09 | acts | GET /api/acts/groups/by/book_id/{book_id} | Get groups by book id | เรียก groups by book | 200 และ list of groups | Passed in pytest; returned group list for book_id 7 | PASS |
| ACT-10 | acts | GET /api/acts/groups/by/group_id/{group_id} | Get group by id | เรียก group by id | 200 และ group object | Covered by pytest; returned group payload | PASS |
| ACT-11 | acts | GET /api/acts/groups/by/act_id/{act_id}/group_number/{group_number} | Get group by act id and number | เรียก group by act id + group number | 200 และ group object | Covered by pytest; returned matching group payload | PASS |
| ACT-12 | acts | GET /api/acts/groups/search/{keyword} | Search groups | เรียก search groups | 200 และรายการ groups ที่ match | Passed in pytest; returned [{id: 22, title: Group Search}] | PASS |
| ACT-13 | acts | GET /api/acts/super_sections/by/act_id/{act_id} | Get super sections by act id | เรียก super sections by act | 200 และ list of super sections | Passed in pytest; returned super section list for act_id 10 | PASS |
| ACT-14 | acts | GET /api/acts/super_sections/by/group_id/{group_id} | Get super sections by group id | เรียก super sections by group | 200 และ list of super sections | Covered by pytest; returned super section payload | PASS |
| ACT-15 | acts | GET /api/acts/super_sections/by/super_section_id/{super_section_id} | Get super section by id | เรียก super section by id | 200 และ super section object | Covered by pytest; returned super section payload | PASS |
| ACT-16 | acts | GET /api/acts/super_sections/by/act_id/{act_id}/super_section_number/{super_section_number} | Get super section by act id and number | เรียก super section by act id + number | 200 และ super section object | Covered by pytest; returned matching super section payload | PASS |
| SEC-01 | sections | GET /api/sections/by/section_id/{section_id} | Get section by id | เรียก section by id | 200 และ section payload | Passed in pytest; returned valid section payload | PASS |
| SEC-02 | sections | GET /api/sections/by/act_id/{act_id} | Get sections by act id | เรียก sections by act | 200 และ list of sections | Passed in pytest; returned section list | PASS |
| SEC-03 | sections | GET /api/sections/by/book_id/{book_id} | Get sections by book id | เรียก sections by book | 200 และ list of sections | Covered by pytest; returned sections payload | PASS |
| SEC-04 | sections | GET /api/sections/by/group_id/{group_id} | Get sections by group id | เรียก sections by group | 200 และ list of sections | Covered by pytest; returned sections payload | PASS |
| SEC-05 | sections | GET /api/sections/by/super_section_id/{super_section_id} | Get sections by super section id | เรียก sections by super section | 200 และ list of sections | Covered by pytest; returned sections payload | PASS |
| SEC-06 | sections | GET /api/sections/by/act_id/{act_id}/section_number/{section_number} | Get section by act id and number | เรียก section by act id + section number | 200 และ section object | Covered by pytest; returned matching section payload | PASS |
| SEC-07 | sections | GET /api/sections/by/act_id/{act_id}/search/{keyword} | Search sections in act | เรียก search sections ภายใน act | 200 และ matching section list | Passed in pytest; returned [{id: 4, act_id: 10, ...}] | PASS |
| SEC-08 | sections | GET /api/sections/search/{keyword} | Search sections across acts | เรียก search sections ทั่วระบบ | 200 และ matching section list | Passed in pytest; returned [{id: 3, act_id: 10, ...}] | PASS |
| LIB-01 | libraries | GET /api/libraries/acts | Library acts | เรียก acts library | 200 และ act list | Passed in pytest; returned [{id: 1, name: Act A}] | PASS |
| LIB-02 | libraries | GET /api/libraries/act/{act_id} | Library act by id | เรียก act library by id | 200 และ act object | Passed in pytest; returned act payload | PASS |
| LIB-03 | libraries | GET /api/libraries/tags | Library tags | เรียก tags | 200 และ tag list | Passed in pytest; returned [{id: 1, name: สำคัญ}] | PASS |
| LIB-04 | libraries | GET /api/libraries/acts/{act_id}/books | Library books by act | เรียก books by act | 200 และ book list | Passed in pytest; returned [{id: 3, act_id: 10, ...}] | PASS |
| LIB-05 | libraries | GET /api/libraries/books/{book_id}/groups | Library groups by book | เรียก groups by book | 200 และ group list | Passed in pytest; returned [{id: 4, book_id: 8, ...}] | PASS |
| LIB-06 | libraries | GET /api/libraries/groups/{group_id}/super_sections | Library super sections by group | เรียก super sections by group | 200 และ super section list | Passed in pytest; returned [{id: 5, group_id: 9, ...}] | PASS |
| LIB-07 | libraries | GET /api/libraries/super_sections/{super_section_id}/sections | Library sections by super section | เรียก sections by super section | 200 และ section list | Passed in pytest; returned [{id: 6, section_number: 5, ...}] | PASS |
| LIB-08 | libraries | GET /api/libraries/sections/{act_id}/{section_number} | Library section by number | เรียก section by act id + number | 200 และ section list | Passed in pytest; returned [{id: 7, section_number: 5, ...}] | PASS |
| LIB-09 | libraries | GET /api/libraries/super_sections/{super_section_id}/sections_stream | Stream library sections | เรียก streaming endpoint | 200 และ NDJSON stream | Passed in pytest; returned section events and done event | PASS |
| CONV-01 | conversations | POST /api/conversations/rooms | Create room | สร้าง chat room | 200 และ room object | Passed in pytest; returned room payload | PASS |
| CONV-02 | conversations | GET /api/conversations/rooms | List rooms | ดึงรายการห้องสนทนา | 200 และ list of rooms | Passed in pytest; returned rooms list | PASS |
| CONV-03 | conversations | GET /api/conversations/rooms/{room_id} | Get room by id | ดึงห้องตาม id | 200 และ room object หรือ 404 ถ้าไม่พบ | Passed in pytest; returned room payload or 404 when missing | PASS |
| CONV-04 | conversations | PUT /api/conversations/rooms/{room_id} | Update room | อัปเดตห้องสนทนา | 200 และ room ที่อัปเดตแล้ว | Passed in pytest; returned updated room payload | PASS |
| CONV-05 | conversations | DELETE /api/conversations/rooms/{room_id} | Delete room | ลบห้องสนทนา | 200 และข้อความยืนยันการลบ | Passed in pytest; returned delete detail | PASS |
| CONV-06 | conversations | DELETE /api/conversations/rooms/by-user/{user_id} | Delete rooms by user | ลบห้องของผู้ใช้ทั้งหมด | 200 และจำนวนห้องที่ลบ | Passed in pytest; returned deleted count | PASS |
| CONV-07 | conversations | POST /api/conversations/rooms/{room_id}/messages | Add message | เพิ่มข้อความในห้อง | 200 และ message object | Passed in pytest; returned inserted message payload | PASS |
| CONV-08 | conversations | GET /api/conversations/rooms/{room_id}/messages | Get messages | ดึงข้อความในห้อง | 200 และ list of messages | Passed in pytest; returned message list | PASS |
| CONV-09 | conversations | GET /api/conversations/rooms/{room_id}/history | Get history | ดึง history สำหรับ LLM | 200 และ history list | Passed in pytest; returned LLM-ready history list | PASS |
| USER-01 | users | POST /api/users/ | Create or update user | สร้างหรืออัปเดต user profile | 200 และ user object | Passed in pytest; returned user payload | PASS |
| USER-02 | users | GET /api/users/{user_id} | Get user | ดึงข้อมูลผู้ใช้ | 200 และ user object หรือ 404 ถ้าไม่พบ | Passed in pytest; returned user payload or 404 when missing | PASS |
| USER-03 | users | PUT /api/users/{user_id} | Update user | อัปเดต user profile | 200 และ user ที่อัปเดตแล้ว | Passed in pytest; returned updated payload | PASS |
| USER-04 | users | DELETE /api/users/{user_id} | Delete user | ลบ user profile | 200 และข้อความยืนยันการลบ | Passed in pytest; returned delete detail | PASS |
| USER-05 | users | GET /api/users/options/jobs | Get jobs options | ดึงรายการ job | 200 และ list of jobs | Passed in pytest; returned jobs list | PASS |
| USER-06 | users | GET /api/users/options/job-types | Get job types options | ดึงรายการ job type | 200 และ list of job types | Passed in pytest; returned job type list | PASS |
| LLM-01 | llm | POST /llm/chat | Chat synchronous | ส่งคำถามไปยัง chat service | 200 และ answer/sources | Passed in pytest; returned {answer: ok, sources: [มาตรา 1]} | PASS |
| LLM-02 | llm | POST /llm/chat_stream | Chat streaming | ส่งคำถามไปยัง chat stream service | 200 และ NDJSON stream หรือ error stream | Passed in pytest; returned content stream and error stream cases | PASS |

## Notes

- เอกสารนี้เป็นรายละเอียดภาคผนวก ใช้ตรวจสอบราย endpoint
- รวม test cases ทั้งหมด 65 รายการ โดย judgments มี 3 cases สำหรับ 2 endpoints
- คอลัมน์ Actual ใช้สรุปผลจาก pytest ล่าสุด

## Test Type Checklist (Mock vs Real Integration)

| Test File | Type | Scope |
| --- | --- | --- |
| `tests/test_services_conversation.py` | Mock/Unit | Service logic ของ conversation |
| `tests/test_routers_conversation.py` | Mock/Integration-like | Conversation routes (contract + error mapping) |
| `tests/test_routers_user.py` | Mock/Integration-like | User routes (contract + validation + error mapping) |
| `tests/test_routers_reference_endpoints.py` | Mock/Integration-like | Acts/Sections/Libraries/LLM routes |
| `tests/test_routers_help_judgment_main.py` | Mock/Integration-like | Help/Judgment/Main utility routes |
