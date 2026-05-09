-- เปิดใช้ extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ===================================
-- ตารางผู้ใช้ (Users) - ใช้ Login ผ่าน Google
-- ===================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id TEXT UNIQUE NOT NULL,         -- Google user ID
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user',               -- เช่น 'user', 'admin'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ===================================
-- ตารางแท็ก (Tags)
-- ===================================
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,              -- เช่น "คอมพิวเตอร์", "แรงงาน", "ละเมิด"
    description TEXT,                       -- คำอธิบาย tag
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===================================
-- ตาราง พระราชบัญญัติ (Acts)
-- ===================================
CREATE TABLE acts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,                    -- ชื่อพระราชบัญญัติ
    preface TEXT,                           -- คำเกริ่นก่อนเข้าสู่มาตรา
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ตารางเชื่อมระหว่าง acts และ tags (Many-to-Many)
CREATE TABLE act_tags (
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (act_id, tag_id)
);

-- ===========================
-- ตาราง บรรพ (Book)
-- ===========================
CREATE TABLE act_books (
    id SERIAL PRIMARY KEY,
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    book_number INT,
    book_title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- ตาราง ลักษณะ (Group)
-- ===========================
CREATE TABLE act_groups (
    id SERIAL PRIMARY KEY,
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    book_id INT REFERENCES act_books(id) ON DELETE SET NULL,
    group_number INT,
    group_title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- ตาราง หมวด (Super Section)
-- ===========================
CREATE TABLE act_super_sections (
    id SERIAL PRIMARY KEY,
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    group_id INT REFERENCES act_groups(id) ON DELETE SET NULL,
    super_number INT,
    super_title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===================================
-- ตาราง มาตราในพระราชบัญญัติ (Act Sections)
-- ===================================
CREATE TABLE act_sections (
    id SERIAL PRIMARY KEY,
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    book_id INT REFERENCES act_books(id) ON DELETE SET NULL,
    group_id INT REFERENCES act_groups(id) ON DELETE SET NULL,
    super_id INT REFERENCES act_super_sections(id) ON DELETE SET NULL,
    section_number INT,                     -- มาตรา
    sub_section TEXT,                       -- มาตราย่อยเลขไทยโบราณหรือทับ (ถ้ามี) เช่น ทวิ, ตรี, /1, /2
    paragraph_number INT,                   -- วรรค (ถ้ามี)
    item_order TEXT,                        -- ลำดับย่อย (ถ้ามี)
    text_original TEXT,                     -- ข้อความต้นฉบับ
    text_processed TEXT,                    -- หลัง preprocessing + การแทนที่อ้างอิง
    embedding VECTOR(1024),                 -- สำหรับ semantic search
    cross_references JSON,                  -- อ้างอิงถึงมาตราอื่นๆ เช่น {10: {"section_number":5, "paragraph_number":2, "item_order":1}}
    external_citations JSON,                -- อ้างอิงภายนอก เช่น {10: {"citation":1}}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_act_sections_embedding 
ON act_sections 
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

CREATE TABLE citations (                    -- อ้างอิงแก้ไขของพระราชบัญญัติ
    act_id INT REFERENCES acts(id) ON DELETE CASCADE,
    reference_number INT,                   -- หมายเลขอ้างอิง
    citation_text TEXT,                     -- ข้อความอ้างอิง
    imported_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (act_id, reference_number)
);


-- ตารางเชื่อมระหว่าง act_sections และ tags
CREATE TABLE act_section_tags (
    act_section_id INT REFERENCES act_sections(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (act_section_id, tag_id)
);

-- ===================================
-- ตาราง คำพิพากษาฎีกา (Judgments)
-- ===================================
CREATE TABLE judgments (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,                    -- ชื่อคดี
    case_number TEXT,                       -- หมายเลขคำพิพากษา
    summary TEXT,                           -- สรุปคดี
    summary_embedding VECTOR(1024),         -- vector ของ summary
    detail TEXT,                            -- รายละเอียดเต็ม
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_judgments_summary_embedding 
ON judgments 
USING ivfflat (summary_embedding vector_l2_ops)
WITH (lists = 100);

-- ตารางเชื่อมระหว่าง judgments และ tags
CREATE TABLE judgment_tags (
    judgment_id INT REFERENCES judgments(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (judgment_id, tag_id)
);

-- ===================================
-- ตารางประวัติการค้น (Query Logs)
-- ===================================
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,                -- คำถามจากผู้ใช้
    query_embedding VECTOR(1024),             -- vector ของ query
    source TEXT,                             -- "acts" | "act_sections" | "judgments"
    top_result_ids INT[],                    -- id ของผลลัพธ์ (optional)
    created_at TIMESTAMP DEFAULT NOW()
);