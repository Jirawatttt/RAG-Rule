/* =============================================================
   app.js — Frontend logic
   ============================================================= */

const API_BASE = "http://localhost:8000";

function goTo(pageId) {
  window.location.href = pageId + ".html";
}

/* ── Submit form ──────────────────────────────────────────── */
async function submitForm() {
  const profile = {};

  const age = parseInt(document.getElementById("inp-age")?.value);
  if (!isNaN(age) && age > 0) profile.age = age;

  const nat = document.getElementById("inp-nationality")?.value;
  if (nat) profile.nationality = nat;

  const ss = document.getElementById("inp-social-security")?.value;
  if (ss) profile.social_security = ss;

  const emp = document.getElementById("inp-employment")?.value;
  if (emp) profile.employment = emp;

  const ch = document.getElementById("inp-children")?.value;
  if (ch) profile.children = ch;

  const dis = document.getElementById("inp-disability")?.value;
  if (dis) profile.disability = dis;

  // ต้องกรอกอย่างน้อย 1 field
  if (Object.keys(profile).length === 0) {
    alert("กรุณากรอกข้อมูลอย่างน้อย 1 ช่อง");
    return;
  }

  sessionStorage.setItem("userProfile", JSON.stringify(profile));

  try {
    const res = await fetch(`${API_BASE}/check-rights`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(profile),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`เกิดข้อผิดพลาด: ${err.detail || res.status}`);
      return;
    }

    const data = await res.json();
    sessionStorage.setItem("benefits", JSON.stringify(data.benefits));
    window.location.href = "result.html";

  } catch (e) {
    alert("ไม่สามารถเชื่อมต่อกับ server ได้");
    console.error(e);
  }
}

function clearForm() {
  ["inp-age","inp-nationality","inp-social-security",
   "inp-children","inp-employment","inp-disability"]
    .forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.value = ""; el.classList.remove("filled","is-invalid"); }
    });
  sessionStorage.removeItem("userProfile");
}

/* ── Highlight chips ──────────────────────────────────────── */
const BENEFIT_HIGHLIGHTS = {
  "เบี้ยยังชีพผู้สูงอายุ":                   [{icon:"💰",label:"600–1,000 บาท/เดือน"},{icon:"🏛️",label:"ติดต่อ อบต./เทศบาล"},{icon:"📋",label:"ใช้บัตรประชาชน"}],
  "เบี้ยความพิการ":                            [{icon:"💰",label:"800 บาท/เดือน"},{icon:"🚌",label:"ลดค่าโดยสาร"},{icon:"📋",label:"ใช้บัตรผู้พิการ"}],
  "สวัสดิการแห่งรัฐ (บัตรคนจน)":              [{icon:"🛒",label:"ค่าสินค้าอุปโภคบริโภค"},{icon:"💡",label:"ค่าน้ำ-ค่าไฟ"},{icon:"🚌",label:"ค่าโดยสาร"}],
  "ประกันสังคม มาตรา 33":                      [{icon:"🏥",label:"รักษาพยาบาลฟรี"},{icon:"👶",label:"สิทธิคลอดบุตร"},{icon:"🛡️",label:"คุ้มครอง 7 กรณี"}],
  "ประกันสังคม มาตรา 39":                      [{icon:"🏥",label:"รักษาพยาบาลฟรี"},{icon:"👴",label:"เงินชราภาพ"},{icon:"🛡️",label:"คุ้มครอง 6 กรณี"}],
  "ประกันสังคม มาตรา 40":                      [{icon:"💰",label:"ส่งสมทบ 70 บาท/เดือน"},{icon:"🏥",label:"เจ็บป่วย-ทุพพลภาพ"},{icon:"👴",label:"เงินชราภาพ"}],
  "เงินอุดหนุนเด็กแรกเกิด":                   [{icon:"💰",label:"600 บาท/เดือน"},{icon:"📅",label:"ถึงอายุ 6 ปี"},{icon:"📋",label:"ใช้สูติบัตรบุตร"}],
  "สิทธิหลักประกันสุขภาพถ้วนหน้า (บัตรทอง)": [{icon:"🏥",label:"รักษาฟรีโรงพยาบาลรัฐ"},{icon:"💊",label:"รับยาฟรี"},{icon:"📋",label:"ใช้บัตรประชาชน"}],
};

function getHighlightBar(name) {
  const chips = BENEFIT_HIGHLIGHTS[name] || [];
  if (!chips.length) return "";
  return `<div class="highlight-bar">${chips.map(c => `<div class="highlight-chip"><span class="chip-icon">${c.icon}</span>${c.label}</div>`).join("")}</div>`;
}

/* ── Render results ───────────────────────────────────────── */
function renderResults(benefits) {
  const container = document.getElementById("result-content");
  if (!benefits || benefits.length === 0) {
    const bar = document.querySelector(".action-bar");
    if (bar) bar.style.display = "none";
    container.innerHTML = `
      <div class="no-result-box">
        <div class="no-result-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="12" stroke="#E0900A" stroke-width="1.5"/>
            <path d="M14 9v6M14 18v1" stroke="#E0900A" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <p class="no-result-heading">ไม่พบสิทธิที่ตรงกับข้อมูลที่กรอก</p>
        <p class="no-result-sub">กรุณากรอกข้อมูลเพิ่มเติม หรือติดต่อหน่วยงานภาครัฐในพื้นที่</p>
      </div>`;
    return;
  }

  container.innerHTML = `
    <section class="rag-hero">
      <div class="rag-kicker">RAG ANALYSIS</div>
      <h2>กำลังวิเคราะห์สิทธิที่เกี่ยวข้อง ${benefits.length} รายการ</h2>
      <p>AI กำลังอ่านเงื่อนไขและข้อมูลอ้างอิงที่ดึงจากฐานความรู้ของระบบ</p>
      <div class="rag-loading"><span></span><span></span><span></span></div>
    </section>`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  }[char]));
}

function renderRagResults(benefits, aiBenefits = [], aiUnavailable = false) {
  const container = document.getElementById("result-content");
  const aiByName = new Map(aiBenefits.map(item => [item.name, item.detail]));
  const cards = benefits.map((benefit, index) => {
    const explanation = aiByName.get(benefit.name);
    const matched = benefit.matched_conditions.map(item => `<li class="rag-match">${escapeHtml(item)}</li>`).join("");
    const missing = benefit.missing_conditions.map(item => `<li class="rag-missing">${escapeHtml(item)}</li>`).join("");
    const documents = benefit.docs.map(item => `<li>${escapeHtml(item)}</li>`).join("");
    const message = explanation
      ? escapeHtml(explanation)
      : aiUnavailable
        ? "ยังไม่สามารถสร้างคำอธิบายจาก AI ได้ แต่รายการด้านล่างเป็นผลจากเงื่อนไขและฐานความรู้ RAG ที่ระบบค้นพบ"
        : "ไม่พบคำอธิบาย AI สำหรับสิทธิ์นี้";
    return `
      <article class="rag-card">
        <div class="rag-card-top"><span>${String(index + 1).padStart(2, "0")}</span><p>สิทธิที่เกี่ยวข้อง</p></div>
        <h3>${escapeHtml(benefit.name)}</h3>
        <div class="rag-answer"><div class="rag-answer-label">คำอธิบายจาก AI + RAG</div><p>${message}</p></div>
        <div class="rag-grid">
          <section><h4>ข้อมูลที่ตรง</h4><ul>${matched || "<li>ระบบยังไม่มีข้อมูลยืนยัน</li>"}</ul></section>
          <section><h4>ควรตรวจเพิ่ม</h4><ul>${missing || "<li class=\"rag-match\">ไม่มีเงื่อนไขค้างจากฟอร์ม</li>"}</ul></section>
        </div>
        <div class="rag-footer"><span>เอกสาร: ${documents || "ตรวจสอบกับหน่วยงาน"}</span>${benefit.link ? `<a href="${escapeHtml(benefit.link)}" target="_blank" rel="noopener noreferrer">แหล่งข้อมูล</a>` : ""}</div>
      </article>`;
  }).join("");
  container.innerHTML = `
    <section class="rag-hero"><div class="rag-kicker">RAG ANALYSIS COMPLETE</div><h2>AI พบสิทธิที่เกี่ยวข้อง ${benefits.length} รายการ</h2><p>คำอธิบายสร้างจากเงื่อนไขและข้อมูลอ้างอิงที่ระบบค้นคืนมา</p></section>
    <div class="rag-results">${cards}</div>`;
}

/* ── Load AI detail (รายละเอียดแต่ละสิทธิ) ─────────────── */
async function loadAIExplanation() {
  const profile = JSON.parse(sessionStorage.getItem("userProfile") || "null");
  if (!profile) return;

  try {
    const res = await fetch(`${API_BASE}/explain`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(profile),
    });
    if (!res.ok) throw new Error("explain failed");

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const text = line.slice(6).trim();
        if (text === "[DONE]" || !text) continue;
        buffer += text;
      }
    }

    if (!buffer) throw new Error("empty AI response");
    const data = JSON.parse(buffer);
    const list = data.benefits || [];
    const benefits = JSON.parse(sessionStorage.getItem("benefits") || "[]");
    renderRagResults(benefits, list);

  } catch (e) {
    console.error("AI explain error:", e);
    const benefits = JSON.parse(sessionStorage.getItem("benefits") || "[]");
    renderRagResults(benefits, [], true);
  }
}
