// main.js — front-end logic สำหรับ Virtual Pet (AI Companion) เวอร์ชันเว็บ Pixel Art
// เรียก REST endpoints ที่ Flask (web/app.py) จัดเตรียมไว้: /api/state, /api/action, /api/interact

const sprite = document.getElementById("sprite");
const petNameEl = document.getElementById("pet-name");
const logMessage = document.getElementById("log-message");
const interactionBox = document.getElementById("interaction-box");
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
  } catch (err) {
    showError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: " + err.message);
  } finally {
    setButtonsDisabled(false);
  }
}

buttons.forEach((btn) => {
  const action = btn.dataset.action;
  if (action) {
    btn.addEventListener("click", () => sendAction(action));
  }
});
document.getElementById("btn-interact").addEventListener("click", doInteract);

loadState();
