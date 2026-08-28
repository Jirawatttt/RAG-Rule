"""
schemas.py — Pydantic models สำหรับ validate request/response
==============================================================
แยกออกมาจาก main.py เพื่อให้ main.py อ่านง่าย
และนำ schema ไปใช้ซ้ำใน test ได้ง่าย
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional

from rules import EmploymentStatus, Nationality, SocialSecurityType, ChildrenStatus


# ---------------------------------------------------------------------------
# Request: POST /api/check
# ---------------------------------------------------------------------------

class UserProfileIn(BaseModel):
    """ข้อมูลที่ frontend ส่งมา — validate ก่อนเข้า rule engine"""

    age: int = Field(..., ge=0, le=120, description="อายุ (0–120 ปี)")
    nationality: Nationality
    social_security: SocialSecurityType
    employment: EmploymentStatus
    children: ChildrenStatus
    has_disability_card: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 65,
                "nationality": "thai",
                "social_security": "none",
                "employment": "unemployed",
                "children": "0",
                "has_disability_card": False,
            }
        }
    }


# ---------------------------------------------------------------------------
# Request: POST /api/explain
# ---------------------------------------------------------------------------

class BenefitItem(BaseModel):
    """สิทธิ 1 รายการที่ rule engine match แล้ว"""
    name:       str
    conditions: list[str]
    detail:     str
    contact:    list[str]
    docs:       list[str]


class ExplainRequest(BaseModel):
    """
    ส่ง profile + benefits มาให้ AI อธิบาย
    rule engine รันฝั่ง frontend แล้ว — ส่งผลมาตรงๆ
    """
    profile:  UserProfileIn
    benefits: list[BenefitItem] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Request: POST /api/log
# ---------------------------------------------------------------------------

class InquiryLog(BaseModel):
    """
    ข้อมูลที่จะบันทึกลง DB
    ไม่เก็บ PII — ไม่มีชื่อ ที่อยู่ เลขบัตร
    """
    profile:          UserProfileIn
    benefits_matched: list[str]          # เก็บแค่ชื่อสิทธิ
    benefit_count:    int
