"""
rules.py — Rule-Based Benefits Engine
======================================
แต่ละ rule ส่งกลับ:
  - matched_conditions : เงื่อนไขที่ user กรอกมาและตรงกัน
  - missing_conditions : เงื่อนไขที่ผูกกับ field ใน form แต่ user ไม่ได้กรอก
  - docs               : เอกสารที่ต้องเตรียม
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Nationality(str, Enum):
    THAI  = "thai"
    OTHER = "other"

class SocialSecurityType(str, Enum):
    SEC_33 = "33"
    SEC_39 = "39"
    SEC_40 = "40"
    NONE   = "none"

class EmploymentStatus(str, Enum):
    EMPLOYED   = "employed"
    SELF       = "self"
    FARMER     = "farmer"
    UNEMPLOYED = "unemployed"

class ChildrenStatus(str, Enum):
    NONE     = "0"
    YOUNG    = "1"
    GROWN_UP = "2"


# ---------------------------------------------------------------------------
# UserProfile — ทุก field เป็น Optional
# ---------------------------------------------------------------------------

@dataclass
class UserProfile:
    age:                 Optional[int]                = None
    nationality:         Optional[Nationality]        = None
    social_security:     Optional[SocialSecurityType] = None
    employment:          Optional[EmploymentStatus]   = None
    children:            Optional[ChildrenStatus]     = None
    has_disability_card: Optional[bool]               = None


# ---------------------------------------------------------------------------
# Benefit — มี matched/missing conditions แยกกัน
# ---------------------------------------------------------------------------

@dataclass
class Benefit:
    name:               str
    matched_conditions: list[str]   # ✓ user กรอกมาและตรงกัน
    missing_conditions: list[str]   # ○ field อยู่ใน form แต่ไม่ได้กรอก
    docs:               list[str]
    contact:            list[str]
    link:               str = ""
    detail:             str = ""    # AI จะเติมทีหลัง


# ---------------------------------------------------------------------------
# Rule functions
# ---------------------------------------------------------------------------

def rule_elderly_allowance(u: UserProfile) -> Optional[Benefit]:
    """เบี้ยยังชีพผู้สูงอายุ — ต้องการ: age >= 60, nationality = thai"""
    matched = []
    missing = []

    # ตรวจ age
    if u.age is not None:
        if u.age >= 60:
            matched.append(f"อายุ 60 ปีขึ้นไป ({u.age} ปี)")
        else:
            return None   # ไม่ผ่าน
    else:
        missing.append("อายุ 60 ปีขึ้นไป")

    # ตรวจ nationality
    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    # ต้องผ่านอย่างน้อย 1 เงื่อนไข
    if not matched:
        return None

    return Benefit(
        name               = "เบี้ยยังชีพผู้สูงอายุ",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["สำเนาบัตรประชาชน", "สำเนาทะเบียนบ้าน", "สมุดบัญชีธนาคาร"],
        contact = ["สำนักงานเทศบาล / อบต. ในพื้นที่", "กรมกิจการผู้สูงอายุ: 02-354-6100"],
        link    = "https://www.dop.go.th/en/topic/view=200",
    )


def rule_disability_allowance(u: UserProfile) -> Optional[Benefit]:
    """เบี้ยความพิการ — ต้องการ: disability = yes, nationality = thai"""
    matched = []
    missing = []

    if u.has_disability_card is not None:
        if u.has_disability_card:
            matched.append("มีบัตรผู้พิการ")
        else:
            return None
    else:
        missing.append("มีบัตรผู้พิการ")

    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    if not matched:
        return None

    return Benefit(
        name               = "เบี้ยความพิการ",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรผู้พิการ", "สำเนาบัตรประชาชน", "สมุดบัญชีธนาคาร"],
        contact = ["สำนักงานเทศบาล / อบต. ในพื้นที่", "กรมส่งเสริมฯ คนพิการ: 02-354-3388"],
        link    = "https://www.dep.go.th/th/rights-welfares-services/disability-allowance",
    )


def rule_welfare_card(u: UserProfile) -> Optional[Benefit]:
    """สวัสดิการแห่งรัฐ — ต้องการ: อายุ 18+, nationality = thai, employment = self/unemployed

    หมายเหตุ: เกณฑ์จริงตัดสินด้วยรายได้/ทรัพย์สิน ซึ่งระบบไม่มี field เก็บ
    จึงใช้ employment เป็น proxy โดยประมาณ (self/unemployed มีแนวโน้มรายได้น้อย)
    ไม่ใช้ FARMER เพราะฟอร์มจริงไม่มี option นี้ให้เลือก
    """
    matched = []
    missing = []

    if u.age is not None:
        if u.age < 18:
            return None
        matched.append(f"อายุ 18 ปีขึ้นไป ({u.age} ปี)")
    else:
        missing.append("อายุ 18 ปีขึ้นไป")

    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    if u.employment is not None:
        if u.employment in {EmploymentStatus.UNEMPLOYED, EmploymentStatus.SELF}:
            matched.append(f"สถานะการทำงาน: {u.employment.value}")
        else:
            return None
    else:
        missing.append("ไม่มีรายได้ประจำ")

    if not matched:
        return None

    return Benefit(
        name               = "สวัสดิการแห่งรัฐ (บัตรคนจน)",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรประชาชน", "เอกสารแสดงรายได้"],
        contact = ["ธนาคารกรุงไทย", "สายด่วนกระทรวงการคลัง: 1359"],
        link    = "https://xn--12cm1ane3a8dcb9a6abq9eehm8a4u7e.mof.go.th",
    )


def rule_social_security_33(u: UserProfile) -> Optional[Benefit]:
    """ประกันสังคม ม.33 — ต้องการ: social_security = 33, employment = employed (ถ้าตอบมา)"""
    matched = []
    missing = []

    if u.social_security is not None:
        if u.social_security == SocialSecurityType.SEC_33:
            matched.append("ลงทะเบียนประกันสังคม มาตรา 33")
        else:
            return None
    else:
        missing.append("ลงทะเบียนประกันสังคม มาตรา 33")

    # guard: ม.33 ต้องมีนายจ้าง — ถ้าตอบ employment มาแล้วขัดกัน ให้ reject
    if u.employment is not None and u.employment != EmploymentStatus.EMPLOYED:
        return None

    if not matched:
        return None

    return Benefit(
        name               = "ประกันสังคม มาตรา 33",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรประชาชน", "หนังสือรับรองจากนายจ้าง"],
        contact = ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        link    = "https://www.themedicative.co/healthcare-rights/social-security/benefit-guide/",
    )


def rule_social_security_39(u: UserProfile) -> Optional[Benefit]:
    """ประกันสังคม ม.39 — ต้องการ: social_security = 39, employment != employed (ถ้าตอบมา)"""
    matched = []
    missing = []

    if u.social_security is not None:
        if u.social_security == SocialSecurityType.SEC_39:
            matched.append("ลงทะเบียนประกันสังคม มาตรา 39")
        else:
            return None
    else:
        missing.append("ลงทะเบียนประกันสังคม มาตรา 39")

    # guard: ม.39 คือคนที่ออกจากงานแล้ว — ถ้าตอบ employment = employed ขัดกัน ให้ reject
    if u.employment is not None and u.employment == EmploymentStatus.EMPLOYED:
        return None

    if not matched:
        return None

    return Benefit(
        name               = "ประกันสังคม มาตรา 39",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรประชาชน", "แบบคำขอ สปส.1-20"],
        contact = ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        link    = "https://www.themedicative.co/healthcare-rights/social-security/benefit-guide/",
    )


def rule_social_security_40(u: UserProfile) -> Optional[Benefit]:
    """ประกันสังคม ม.40 — ต้องการ: social_security=40 หรือ (ไม่มีประกัน + employment != employed), nationality=thai, age 15-65"""
    matched = []
    missing = []

    if u.social_security is not None:
        if u.social_security == SocialSecurityType.SEC_40:
            matched.append("ลงทะเบียนประกันสังคม มาตรา 40")
        elif u.social_security != SocialSecurityType.NONE:
            return None  # เป็น ม.33/39 อยู่แล้ว ไม่เข้าเกณฑ์ ม.40
        else:
            # social_security = none แล้ว ต้องดูอาชีพต่อว่าเป็นอาชีพอิสระหรือไม่
            if u.employment is not None:
                if u.employment == EmploymentStatus.EMPLOYED:
                    return None  # เป็นลูกจ้างในระบบ ไม่ใช่อาชีพอิสระ
                matched.append(f"ไม่มีประกันสังคม + ประกอบอาชีพอิสระ ({u.employment.value})")
            else:
                missing.append("สถานะการทำงาน (เพื่อตรวจว่าประกอบอาชีพอิสระ)")
    else:
        missing.append("ประกันสังคม มาตรา 40 (อาชีพอิสระ)")

    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    if u.age is not None:
        if 15 <= u.age <= 65:
            matched.append(f"อายุ 15–65 ปี ({u.age} ปี)")
        else:
            return None
    else:
        missing.append("อายุ 15–65 ปี")

    if not matched:
        return None

    return Benefit(
        name               = "ประกันสังคม มาตรา 40",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรประชาชน"],
        contact = ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        link    = "https://www.themedicative.co/healthcare-rights/social-security/benefit-guide/",
    )


def rule_newborn_subsidy(u: UserProfile) -> Optional[Benefit]:
    """เงินอุดหนุนเด็กแรกเกิด — ต้องการ: children = 1, nationality = thai"""
    matched = []
    missing = []

    if u.children is not None:
        if u.children == ChildrenStatus.YOUNG:
            matched.append("มีบุตรอายุ 0–6 ปี")
        else:
            return None
    else:
        missing.append("มีบุตรอายุ 0–6 ปี")

    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    if not matched:
        return None

    return Benefit(
        name               = "เงินอุดหนุนเด็กแรกเกิด",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["สูติบัตรบุตร", "สำเนาบัตรประชาชนผู้ปกครอง", "สมุดบัญชีธนาคาร"],
        contact = ["สำนักงานพัฒนาสังคมและความมั่นคงของมนุษย์จังหวัด", "สายด่วน: 1300"],
        link    = "https://th.jobsdb.com/th/career-advice/article/child-support-grant",
    )


def rule_universal_health(u: UserProfile) -> Optional[Benefit]:
    """บัตรทอง — ต้องการ: nationality = thai, social_security != 33/39"""
    matched = []
    missing = []

    if u.nationality is not None:
        if u.nationality == Nationality.THAI:
            matched.append("สัญชาติไทย")
        else:
            return None
    else:
        missing.append("สัญชาติไทย")

    if u.social_security is not None:
        if u.social_security not in {SocialSecurityType.SEC_33, SocialSecurityType.SEC_39}:
            matched.append("ไม่ได้อยู่ในระบบประกันสังคม ม.33/39")
        else:
            return None
    else:
        missing.append("ไม่ได้อยู่ในระบบประกันสังคม ม.33/39")

    if not matched:
        return None

    return Benefit(
        name               = "สิทธิหลักประกันสุขภาพถ้วนหน้า (บัตรทอง)",
        matched_conditions = matched,
        missing_conditions = missing,
        docs    = ["บัตรประชาชน"],
        contact = ["โรงพยาบาลรัฐตามทะเบียนบ้าน", "สายด่วน สปสช.: 1330"],
        link    = "https://www.nhso.go.th/th/component/content/article/2024-08-22-03-32-58?Itemid=426",
    )


# ---------------------------------------------------------------------------
# Rule registry + engine
# ---------------------------------------------------------------------------

RULES = [
    rule_elderly_allowance,
    rule_disability_allowance,
    rule_welfare_card,
    rule_social_security_33,
    rule_social_security_39,
    rule_social_security_40,
    rule_newborn_subsidy,
    rule_universal_health,
]


def check_rights(profile: UserProfile) -> list[Benefit]:
    return [b for fn in RULES if (b := fn(profile)) is not None]