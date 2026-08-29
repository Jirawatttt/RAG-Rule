"""OpenAI generation and embedding client for the RAG workflow."""

import os
import asyncio
import logging
from typing import AsyncGenerator
from dotenv import load_dotenv
from openai import AsyncOpenAI
from models import UserProfile, Benefit

load_dotenv()
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _build_prompt(profile: UserProfile, benefits: list[Benefit]) -> str:
    employment_th = {
        "employed":   "ลูกจ้าง",
        "self":       "อาชีพอิสระ",
        "unemployed": "ว่างงาน",
    }.get(profile.employment.value if profile.employment else "", "ไม่ระบุ")

    age_str = f"{profile.age} ปี" if profile.age else "ไม่ระบุ"

    # สร้างรายการสิทธิ + context สำหรับ AI
    benefits_text = ""
    for i, b in enumerate(benefits, 1):
        benefits_text += f"\n{i}. {b.name}\n"
        benefits_text += f"   เงื่อนไขที่ตรงกัน: {', '.join(b.matched_conditions) or 'ไม่ระบุ'}\n"
        benefits_text += f"   เอกสารที่ต้องใช้: {', '.join(b.docs)}\n"
        benefits_text += f"   ติดต่อ: {', '.join(b.contact)}\n"
        benefits_text += f"   หลักฐานจากระบบ RAG: {b.detail or 'ไม่มี'}\n"

    return f"""คุณเป็นผู้ช่วยอธิบายสิทธิประโยชน์ภาครัฐ

ข้อมูลผู้ใช้: อายุ {age_str}, สถานะ {employment_th}

สิทธิที่ระบบตรวจพบ {len(benefits)} รายการ:
{benefits_text}

กรุณาเขียนคำอธิบายสั้นๆ สำหรับแต่ละสิทธิ โดย:
- อธิบายว่าสิทธินี้คืออะไร ได้รับอะไร จำนวนเท่าไหร่
- บอกขั้นตอนการสมัครหรือยื่นเรื่องเบื้องต้น
- ใช้ภาษาไทยเข้าใจง่าย ไม่เป็นทางการ
- ห้ามใช้ markdown เช่น ** หรือ ##
- ใช้ข้อมูลจาก "หลักฐานจากระบบ RAG" เป็นแหล่งอ้างอิงสำหรับรายละเอียด
- หากมีเงื่อนไขที่ยังไม่ระบุ ให้บอกผู้ใช้ว่าต้องตรวจสอบเพิ่มเติม ห้ามยืนยันสิทธิ์
- ห้ามแต่งข้อมูลที่ไม่มีในรายการด้านบน
- อธิบายให้ครบทุกสิทธิในรายการ

ตอบในรูปแบบ JSON เท่านั้น ไม่มี markdown ไม่มี backtick:
{{"benefits": [{{"name": "ชื่อสิทธิ", "detail": "คำอธิบาย"}}]}}"""


async def _call_model(model: str, prompt: str) -> str:
    if client is None:
        raise RuntimeError("ไม่พบ OPENAI_API_KEY ใน .env")
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "ตอบตามข้อมูลที่ให้เท่านั้น และคืน JSON ที่ valid เสมอ"},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=2048,
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


async def embed_text(text: str) -> list[float]:
    """Create an embedding for a RAG query or document chunk."""
    if client is None:
        raise RuntimeError("ไม่พบ OPENAI_API_KEY ใน .env")
    response = await client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


async def explain_benefits(
    profile:  UserProfile,
    benefits: list[Benefit],
) -> AsyncGenerator[str, None]:
    prompt     = _build_prompt(profile, benefits)
    last_error = None

    for attempt in range(1, 3):
        try:
            logger.info(f"Calling OpenAI [{MODEL}] attempt {attempt}")
            text = await _call_model(MODEL, prompt)
            if text:
                import json
                data = json.loads(text)
                yield json.dumps(data, ensure_ascii=False)
                return
            yield '{"benefits":[]}'
            return
        except Exception as e:
            last_error = e
            logger.error(f"OpenAI error [{MODEL}] attempt {attempt}: {e}")
            if attempt < 2 and ("429" in str(e) or "503" in str(e)):
                await asyncio.sleep(2)
                continue
            break

    logger.error(f"All models failed: {last_error}")
    yield '{"benefits":[],"error":"AI ไม่พร้อมใช้งานในขณะนี้"}'
