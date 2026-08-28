# ระบบแสดงสิทธิประโยชน์ภาครัฐเบื้องต้น

## โครงสร้างโปรเจค
```
rights-project/
├── frontend/       ← HTML + CSS + JS
│   ├── home.html
│   ├── input.html
│   ├── result.html
│   ├── styles.css
│   └── app.js
│
└── backend/        ← FastAPI + Python
    ├── main.py     ← routes
    ├── rules.py    ← rule engine
    ├── llm.py      ← Gemini AI
    ├── database.py ← PostgreSQL
    ├── requirements.txt
    └── .env.example
```

---

## โครงสร้าง RAG ใหม่

ระบบยังรับข้อมูลจากฟอร์มเดิม แต่เปลี่ยนแหล่งเงื่อนไขจาก `rules.py`
ไปเป็น PostgreSQL เพื่อให้แก้ไขได้โดยไม่ต้องแก้โค้ด

```
User form → metadata filter จาก DB → retrieve เอกสารที่เกี่ยวข้อง
          → OpenAI อธิบายผลจากหลักฐาน RAG → result.html
```

ตอน backend เริ่มทำงานครั้งแรก ระบบจะสร้างและ seed ตารางต่อไปนี้อัตโนมัติ:

- `benefits` — ข้อมูลสิทธิ์, เอกสาร, ช่องทางติดต่อ และลิงก์
- `benefit_conditions` — เงื่อนไขที่ใช้ match (`field_name`, `operator`, `expected_value`)
- `benefit_documents` — เนื้อหาที่ retriever ส่งให้ AI อธิบาย

### แก้ข้อมูลภายหลัง

แก้ข้อมูลผ่าน DB เป็นหลักได้เลย โดย seed จาก `rag_catalog.py` จะทำงานเฉพาะ
เมื่อฐานข้อมูลยังไม่มีสิทธิ์ จึงไม่ทับการแก้ไขใน DB ของคุณ

- เพิ่มสิทธิ์: เพิ่มแถวใน `benefits` แล้วเพิ่มเงื่อนไขและเอกสารที่ผูกกับ `benefit_id`
- ปรับเกณฑ์: แก้ `benefit_conditions.expected_value` หรือ `operator`
- ปรับคำอธิบาย RAG: แก้ `benefit_documents.content`
- ปิดสิทธิ์ชั่วคราว: ตั้ง `benefits.active = false`

operator ที่รองรับในเวอร์ชันแรกคือ `eq`, `gte`, `between`, `in`, `not_in`
และ `manual` สำหรับข้อมูลที่ฟอร์มปัจจุบันยังไม่ได้ถาม ระบบจะแสดงเป็น
"ควรตรวจสอบเพิ่มเติม" แทนการยืนยันสิทธิ์

### OpenAI configuration

```env
OPENAI_API_KEY=ใส่คีย์จาก OpenAI Platform
OPENAI_MODEL=gpt-5.6-luna
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

ระบบใช้ `gpt-5.6-luna` สร้างคำอธิบาย และใช้
`text-embedding-3-small` สร้าง vector ของเอกสาร RAG เมื่อมีการค้นครั้งแรก
embedding จะถูกเก็บไว้ใน `benefit_documents.embedding` เพื่อไม่ต้องสร้างซ้ำทุกครั้ง

---

## วิธีรันบนเครื่อง (Local)

### สิ่งที่ต้องมีก่อน
- Python 3.11+
- PostgreSQL (ติดตั้งแล้วรันอยู่)
- Gemini API key (ฟรี) → https://aistudio.google.com/app/apikey
- VS Code + extension "Live Server"

---

### ขั้นตอนที่ 1 — ตั้งค่า PostgreSQL

```sql
-- เปิด psql แล้วรัน
CREATE DATABASE rights_db;
```

---

### ขั้นตอนที่ 2 — ตั้งค่า Backend

```bash
cd backend

# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# สร้างไฟล์ .env
cp .env.example .env
```

แก้ไข `.env` ใส่ค่าจริง:
```
DATABASE_URL=postgresql+asyncpg://postgres:รหัสผ่านของคุณ@localhost:5432/rights_db
GEMINI_API_KEY=ใส่ key ที่ได้จาก Google AI Studio
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

---

### ขั้นตอนที่ 3 — รัน Backend

```bash
# อยู่ใน folder backend และ venv เปิดอยู่
uvicorn main:app --reload
```

เห็นข้อความนี้ = สำเร็จ ✅
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Database connected — tables ready
```

ทดสอบ API ได้ที่ → http://localhost:8000/docs

---

### ขั้นตอนที่ 4 — รัน Frontend

เปิด VS Code → คลิกขวาที่ `frontend/home.html` → **Open with Live Server**

เบราว์เซอร์จะเปิดที่ → http://localhost:5500/home.html

---

### ทดสอบระบบ

1. เปิด http://localhost:5500/home.html
2. กด "เริ่มต้นใช้งาน"
3. กรอกข้อมูล เช่น อายุ 65, สัญชาติไทย, ว่างงาน, ไม่มีประกันสังคม
4. กด "ตรวจสอบสิทธิ"
5. ดูการ์ดสิทธิ + AI อธิบาย (stream)

ตรวจสอบ DB ว่ามีข้อมูลเข้า:
```
http://localhost:8000/stats
```

---

## หากเจอปัญหา

**backend ขึ้น error "asyncpg"**
→ ตรวจสอบว่า PostgreSQL รันอยู่ และ DATABASE_URL ใน .env ถูกต้อง

**หน้าเว็บขึ้น "ไม่สามารถเชื่อมต่อกับ server"**
→ ตรวจสอบว่า uvicorn รันอยู่ที่ port 8000

**AI ไม่แสดงคำอธิบาย**
→ ตรวจสอบ GEMINI_API_KEY ใน .env
