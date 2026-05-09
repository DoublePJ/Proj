# Backend Test Case Matrix (Summary - One Page)

เอกสารนี้เป็นสรุป 1 หน้า สำหรับส่งงาน โดยแสดงภาพรวมการครอบคลุม endpoint ทั้งหมดใน backend

อ้างอิงผลการรันล่าสุด:
- pytest passed: 88 tests

| Module | Endpoints Covered | Coverage Focus | Current Result |
| --- | ---: | --- | --- |
| utility | 4 | root, health, warmup, llm-router enable | PASS |
| help | 8 | help discovery endpoints ทั้งชุด | PASS |
| judgments | 2 endpoints, 3 cases | list and detail (+ not found behavior) | PASS |
| acts | 16 | read/search hierarchy: act, book, group, super section | PASS |
| sections | 8 | read/search sections across act structure | PASS |
| libraries | 9 | tree-navigation endpoints + ndjson stream | PASS |
| conversations | 9 | room lifecycle, message flow, history, error mapping | PASS |
| users | 6 | profile CRUD + options endpoints | PASS |
| llm | 2 | chat sync + chat stream (success and failure path) | PASS |

| Metric | Value |
| --- | --- |
| Total modules covered | 9 |
| Total endpoints covered | 64 |
| Automated test status | PASS |

## Deliverable Split

- Summary (one page): this file
- Detailed appendix: `TEST_CASES_APPENDIX.md`

## Notes

- เวอร์ชันสรุปนี้ย่อจากตารางละเอียดเพื่อให้อ่านเร็วสำหรับรายงานหลัก
- ตัวเลขในไฟล์นี้นับเป็น endpoint coverage; appendix แยกนับเป็น test cases ได้มากกว่าเพราะบาง endpoint มีหลายกรณีทดสอบ
- ราย endpoint (Act/Expected/Actual ระดับละเอียด) อยู่ในภาคผนวก
