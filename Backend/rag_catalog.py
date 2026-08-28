"""Initial data for the rights catalogue.

This file only bootstraps an empty database.  After the first start, edit the
benefit, benefit_condition and benefit_document tables instead of editing code.
"""

BENEFIT_CATALOG = [
    {
        "slug": "elderly_allowance",
        "name": "เบี้ยยังชีพผู้สูงอายุ",
        "category": "elderly",
        "docs": ["สำเนาบัตรประชาชน", "สำเนาทะเบียนบ้าน", "สมุดบัญชีธนาคาร"],
        "contact": ["สำนักงานเทศบาล / อบต. ในพื้นที่", "กรมกิจการผู้สูงอายุ: 02-354-6100"],
        "link": "https://www.dop.go.th/en/topic/view=200",
        "conditions": [
            ("อายุ 60 ปีขึ้นไป", "age", "gte", 60, True),
            ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("มีชื่อในทะเบียนบ้านในเขตที่จะยื่น", None, "manual", None, False),
            ("ไม่ได้รับบำนาญหรือสวัสดิการรัฐที่ซ้ำซ้อน", None, "manual", None, False),
        ],
        "document": "เบี้ยยังชีพผู้สูงอายุ: ผู้ขอควรมีอายุ 60 ปีขึ้นไปและสัญชาติไทย โดยต้องตรวจสอบทะเบียนบ้านในเขต อปท. ที่ยื่นคำขอ และสถานะบำนาญหรือสวัสดิการรัฐที่อาจซ้ำซ้อนก่อนยืนยันสิทธิ์.",
    },
    {
        "slug": "disability_allowance", "name": "เบี้ยความพิการ", "category": "disability",
        "docs": ["บัตรผู้พิการ", "สำเนาบัตรประชาชน", "สมุดบัญชีธนาคาร"],
        "contact": ["สำนักงานเทศบาล / อบต. ในพื้นที่", "กรมส่งเสริมฯ คนพิการ: 02-354-3388"],
        "link": "https://www.dep.go.th/th/rights-welfares-services/disability-allowance",
        "conditions": [
            ("มีบัตรผู้พิการ", "disability", "eq", "yes", True),
            ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("มีชื่อในทะเบียนบ้านในพื้นที่ที่ยื่น", None, "manual", None, False),
        ],
        "document": "เบี้ยความพิการ: ตรวจบัตรประจำตัวผู้พิการ สัญชาติไทย และทะเบียนบ้านในพื้นที่ที่ยื่นคำขอ ก่อนยืนยันสิทธิ์.",
    },
    {
        "slug": "state_welfare_card", "name": "สวัสดิการแห่งรัฐ (บัตรคนจน)", "category": "income_support",
        "docs": ["บัตรประชาชน", "เอกสารแสดงรายได้"],
        "contact": ["ธนาคารกรุงไทย", "สายด่วนกระทรวงการคลัง: 1359"],
        "link": "https://xn--12cm1ane3a8dcb9a6abq9eehm8a4u7e.mof.go.th",
        "conditions": [
            ("อายุ 18 ปีขึ้นไป", "age", "gte", 18, True), ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("รายได้ส่วนบุคคลไม่เกินเกณฑ์", None, "manual", None, False),
            ("รายได้และทรัพย์สินครัวเรือนผ่านเกณฑ์", None, "manual", None, False),
        ],
        "document": "สวัสดิการแห่งรัฐต้องตรวจอายุ สัญชาติ รายได้ส่วนบุคคล รายได้เฉลี่ยครัวเรือน ทรัพย์สิน และข้อยกเว้นตามประกาศรอบรับสมัคร จึงเป็นเพียงการประเมินเบื้องต้นหากยังไม่มีข้อมูลการเงิน.",
    },
    {
        "slug": "social_security_33", "name": "ประกันสังคม มาตรา 33", "category": "social_security",
        "docs": ["บัตรประชาชน", "หนังสือรับรองจากนายจ้าง"],
        "contact": ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        "link": "https://www.sso.go.th", "conditions": [
            ("เป็นผู้ประกันตน มาตรา 33", "social_security", "eq", "33", True),
            ("เป็นลูกจ้างมีนายจ้าง", "employment", "eq", "employed", True),
        ], "document": "ประกันสังคมมาตรา 33 สำหรับลูกจ้างที่มีนายจ้างและขึ้นทะเบียนกับสำนักงานประกันสังคม. การสมัครครั้งแรกมีเงื่อนไขอายุที่หน่วยงานตรวจสอบ.",
    },
    {
        "slug": "social_security_39", "name": "ประกันสังคม มาตรา 39", "category": "social_security",
        "docs": ["บัตรประชาชน", "แบบคำขอ สปส.1-20"],
        "contact": ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        "link": "https://www.sso.go.th", "conditions": [
            ("เป็นผู้ประกันตน มาตรา 39", "social_security", "eq", "39", True),
            ("เคยเป็นผู้ประกันตน ม.33 อย่างน้อย 12 เดือน", None, "manual", None, False),
            ("ลาออกจากงานไม่เกินระยะที่กำหนด", None, "manual", None, False),
        ], "document": "ประกันสังคมมาตรา 39 ต้องเคยเป็นผู้ประกันตนมาตรา 33 ตามระยะเวลาที่กำหนด และสมัครต่อภายในระยะเวลาหลังออกจากงาน. สำนักงานประกันสังคมเป็นผู้ยืนยันข้อมูลนี้.",
    },
    {
        "slug": "social_security_40", "name": "ประกันสังคม มาตรา 40", "category": "social_security",
        "docs": ["บัตรประชาชน"], "contact": ["สำนักงานประกันสังคมในพื้นที่", "สายด่วน: 1506"],
        "link": "https://www.sso.go.th", "conditions": [
            ("อายุ 15–65 ปี", "age", "between", [15, 65], True),
            ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("ไม่เป็นผู้ประกันตน ม.33/39", "social_security", "not_in", ["33", "39"], True),
            ("ประกอบอาชีพอิสระหรือว่างงาน", "employment", "in", ["self", "unemployed"], True),
        ], "document": "ประกันสังคมมาตรา 40 เหมาะกับผู้ประกอบอาชีพอิสระที่ไม่เป็นผู้ประกันตนมาตรา 33 หรือ 39 มีสัญชาติไทย และอายุ 15–65 ปี.",
    },
    {
        "slug": "newborn_subsidy", "name": "เงินอุดหนุนเด็กแรกเกิด", "category": "family",
        "docs": ["สูติบัตรบุตร", "สำเนาบัตรประชาชนผู้ปกครอง", "สมุดบัญชีธนาคาร"],
        "contact": ["สำนักงานพัฒนาสังคมและความมั่นคงของมนุษย์จังหวัด", "สายด่วน: 1300"],
        "link": "https://csgproject.dcy.go.th", "conditions": [
            ("มีบุตรอายุ 0–6 ปี", "children", "eq", "1", True), ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("รายได้เฉลี่ยครัวเรือนไม่เกินเกณฑ์", None, "manual", None, False),
            ("เป็นผู้ปกครองหรือดูแลเด็กจริง", None, "manual", None, False),
        ], "document": "เงินอุดหนุนเด็กแรกเกิดต้องตรวจอายุเด็ก สัญชาติ รายได้เฉลี่ยครัวเรือน และสถานะผู้ปกครองหรือผู้ดูแลเด็กจริง.",
    },
    {
        "slug": "universal_health", "name": "สิทธิหลักประกันสุขภาพถ้วนหน้า (บัตรทอง)", "category": "healthcare",
        "docs": ["บัตรประชาชน"], "contact": ["โรงพยาบาลรัฐตามทะเบียนบ้าน", "สายด่วน สปสช.: 1330"],
        "link": "https://www.nhso.go.th", "conditions": [
            ("สัญชาติไทย", "nationality", "eq", "thai", True),
            ("ไม่อยู่ในประกันสังคม ม.33/39", "social_security", "not_in", ["33", "39"], True),
            ("ไม่มีสิทธิรักษาพยาบาลรัฐอื่นซ้ำซ้อน", None, "manual", None, False),
        ], "document": "สิทธิหลักประกันสุขภาพถ้วนหน้าต้องไม่มีสิทธิสวัสดิการรักษาพยาบาลอื่นซ้ำซ้อน เช่น มาตรา 33/39 หรือสิทธิข้าราชการ. หน่วยงานจะตรวจสิทธิจริงก่อนรับบริการ.",
    },
]
