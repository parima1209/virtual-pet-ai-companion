// main.js — front-end logic สำหรับ Virtual Pet (AI Companion) เวอร์ชันเว็บ Pixel Art
// เรียก REST endpoints ที่ Flask (web/app.py) จัดเตรียมไว้: /api/state, /api/action, /api/interact

const sprite = document.getElementById("sprite");
const petNameEl = document.getElementById("pet-name");
const logMessage = document.getElementById("log-message");
const interactionBox = document.getElementById("interaction-box");
const neglectBanner = document.getElementById("neglect-banner");
const buttons = document.querySelectorAll(".pixel-btn");

const bars = {
  hunger: document.getElementById("bar-hunger"),
  mood: document.getElementById("bar-mood"),
  energy: document.getElementById("bar-energy"),
};
const vals = {
  hunger: document.getElementById("val-hunger"),
  mood: document.getElementById("val-mood"),
  energy: document.getElementById("val-energy"),
};

function setButtonsDisabled(disabled) {
  buttons.forEach((b) => { b.disabled = disabled; });
}

function renderState(state) {
  petNameEl.textContent = state.name;
  sprite.src = `/static/sprites/pet_${state.sprite}.png`;
  sprite.classList.add("bump");
  setTimeout(() => sprite.classList.remove("bump"), 150);

  ["hunger", "mood", "energy"].forEach((key) => {
    const v = Math.max(0, Math.min(100, state[key]));
    bars[key].style.width = v + "%";
    vals[key].textContent = v;
  });

  if (state.message) {
    logMessage.textContent = state.message;
    logMessage.classList.remove("log-error");
  }

  // Sprint 3: เตือนเมื่อสัตว์เลี้ยงถูกปล่อยไว้นานจนหิวมาก/พลังงานหมด
  if (state.neglected && state.warning) {
    neglectBanner.textContent = "⚠️ " + state.warning;
    neglectBanner.hidden = false;
  } else {
    neglectBanner.hidden = true;
  }
}

function showError(text) {
  logMessage.textContent = text;
  logMessage.classList.add("log-error");
}

function renderInteraction(interaction, source) {
  interactionBox.hidden = false;
  if (interaction.kind === "image") {
    interactionBox.innerHTML = `
      <img src="${interaction.url}" alt="รูปสุ่มจาก ${source}">
      <div class="source-tag">source: ${source}</div>
    `;
  } else if (interaction.kind === "fact") {
    interactionBox.innerHTML = `
      <p class="fact-text">"${interaction.text}"</p>
      <div class="source-tag">source: ${source}</div>
    `;
  }
}

async function loadState() {
  try {
    const res = await fetch("/api/state");
    if (!res.ok) throw new Error("โหลดสถานะไม่สำเร็จ");
    const state = await res.json();
    renderState(state);
  } catch (err) {
    showError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: " + err.message);
  }
}

async function sendAction(action) {
  setButtonsDisabled(true);
  try {
    const res = await fetch("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "เกิดข้อผิดพลาด");
      return;
    }
    renderState(data);
  } catch (err) {
    showError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: " + err.message);
  } finally {
    setButtonsDisabled(false);
  }
}

async function doInteract() {
  setButtonsDisabled(true);
  interactionBox.hidden = true;
  logMessage.textContent = "กำลังเชื่อมต่อ API เพื่อดึงการโต้ตอบพิเศษ...";
  logMessage.classList.remove("log-error");
  try {
    const res = await fetch("/api/interact");
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "เชื่อมต่อ API ไม่สำเร็จ");
      return;
    }
    renderState(data);
    renderInteraction(data.interaction, data.source);
    // ถ้าแผงประวัติเปิดอยู่ ให้รีเฟรชประวัติทันทีเพื่อเห็นรายการล่าสุด
    if (!historyContent.hidden) loadHistory();
  } catch (err) {
    showError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: " + err.message);
  } finally {
    setButtonsDisabled(false);
  }
}

// ---------------------------------------------------------------------------
// Sprint 2 — แผงประวัติการโต้ตอบ: Search / Filter / Sort ผ่าน /api/history
// ---------------------------------------------------------------------------
const historyToggleBtn = document.getElementById("btn-history");
const historyContent = document.getElementById("history-content");
const historySearch = document.getElementById("history-search");
const historySource = document.getElementById("history-source");
const historyKind = document.getElementById("history-kind");
const historyOrder = document.getElementById("history-order");
const historyList = document.getElementById("history-list");

function renderHistory(items) {
  historyList.innerHTML = "";
  if (items.length === 0) {
    const li = document.createElement("li");
    li.className = "history-empty";
    li.textContent = "ยังไม่มีประวัติที่ตรงเงื่อนไข ลองกด Interact ดูก่อนนะ";
    historyList.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.className = "history-item";
    const snippet = item.kind === "image" ? "🖼️ ได้รูปภาพใหม่" : `"${item.content}"`;
    const time = (item.timestamp || "").replace("T", " ").slice(0, 19);
    li.innerHTML = `<span class="history-time">${time}</span> ` +
      `<span class="history-source">${item.source}</span> ${snippet}`;
    historyList.appendChild(li);
  });
}

async function loadHistory() {
  const params = new URLSearchParams();
  if (historySearch.value.trim()) params.set("q", historySearch.value.trim());
  if (historySource.value) params.set("source", historySource.value);
  if (historyKind.value) params.set("kind", historyKind.value);
  params.set("order", historyOrder.value);

  try {
    const res = await fetch("/api/history?" + params.toString());
    const data = await res.json();
    renderHistory(data.results || []);
  } catch (err) {
    historyList.innerHTML = "";
    const li = document.createElement("li");
    li.className = "history-empty";
    li.textContent = "โหลดประวัติไม่สำเร็จ: " + err.message;
    historyList.appendChild(li);
  }
}

historyToggleBtn.addEventListener("click", () => {
  historyContent.hidden = !historyContent.hidden;
  if (!historyContent.hidden) loadHistory();
});
[historySearch, historySource, historyKind, historyOrder].forEach((el) => {
  el.addEventListener("input", loadHistory);
  el.addEventListener("change", loadHistory);
});

buttons.forEach((btn) => {
  const action = btn.dataset.action;
  if (action) {
    btn.addEventListener("click", () => sendAction(action));
  }
});
document.getElementById("btn-interact").addEventListener("click", doInteract);

// ---------------------------------------------------------------------------
// Final Sprint — AI Advisor (rule-based): /api/advice
// ---------------------------------------------------------------------------
const adviceToggleBtn = document.getElementById("btn-advice");
const adviceContent = document.getElementById("advice-content");
const adviceHeadline = document.getElementById("advice-headline");
const adviceScore = document.getElementById("advice-score");
const adviceRecent = document.getElementById("advice-recent");

async function loadAdvice() {
  adviceHeadline.textContent = "กำลังวิเคราะห์...";
  try {
    const res = await fetch("/api/advice");
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "โหลดคำแนะนำไม่สำเร็จ");
    adviceHeadline.textContent = data.headline;
    adviceScore.textContent = `คะแนนความเป็นอยู่ ${data.score}/100`;
    adviceRecent.textContent = `Interact ใน 30 นาทีล่าสุด: ${data.recent_interactions_30min} ครั้ง`;
  } catch (err) {
    adviceHeadline.textContent = "โหลดคำแนะนำไม่สำเร็จ: " + err.message;
    adviceScore.textContent = "";
    adviceRecent.textContent = "";
  }
}

adviceToggleBtn.addEventListener("click", () => {
  adviceContent.hidden = !adviceContent.hidden;
  if (!adviceContent.hidden) loadAdvice();
});

loadState();
