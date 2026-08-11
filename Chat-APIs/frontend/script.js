// Chat UI logic: session handling, API calls, rendering, persistence.
// Depends on config.js being loaded first (defines APP_CONFIG).

const STORAGE_KEY_SESSION_ID = "chat_session_id";
const STORAGE_KEY_HISTORY = "chat_history";
const STORAGE_KEY_THEME = "chat_theme";

const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-chat-btn");
const typingIndicatorEl = document.getElementById("typing-indicator");
const themeToggleBtn = document.getElementById("theme-toggle-btn");
const emptyStateEl = document.getElementById("empty-state");

const AVATAR_LABEL = { user: "U", assistant: "AI", error: "!" };

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  themeToggleBtn.textContent = theme === "dark" ? "🌙 Dark" : "☀️ Light";
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  localStorage.setItem(STORAGE_KEY_THEME, next);
  applyTheme(next);
}

applyTheme(localStorage.getItem(STORAGE_KEY_THEME) || "dark");
themeToggleBtn.addEventListener("click", toggleTheme);

function getOrCreateSessionId() {
  let sessionId = localStorage.getItem(STORAGE_KEY_SESSION_ID);
  if (!sessionId) {
    sessionId = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(STORAGE_KEY_SESSION_ID, sessionId);
  }
  return sessionId;
}

function loadHistory() {
  const raw = localStorage.getItem(STORAGE_KEY_HISTORY);
  return raw ? JSON.parse(raw) : [];
}

function saveHistory(history) {
  localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(history));
}

let sessionId = getOrCreateSessionId();
let history = loadHistory();

function renderMessage(role, content) {
  emptyStateEl.classList.add("hidden");

  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = AVATAR_LABEL[role] || "?";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollToBottom();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderAll() {
  messagesEl.innerHTML = "";
  messagesEl.appendChild(emptyStateEl);
  emptyStateEl.classList.toggle("hidden", history.length > 0);
  history.forEach((msg) => renderMessage(msg.role, msg.content));
}

function setLoading(isLoading) {
  typingIndicatorEl.classList.toggle("hidden", !isLoading);
  sendBtn.disabled = isLoading;
  if (isLoading) scrollToBottom();
}

function autoResizeTextarea() {
  inputEl.style.height = "auto";
  inputEl.style.height = `${inputEl.scrollHeight}px`;
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = "";
  autoResizeTextarea();

  history.push({ role: "user", content: text });
  saveHistory(history);
  renderMessage("user", text);

  setLoading(true);

  try {
    const res = await fetch(`${APP_CONFIG.API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });

    const data = await res.json();

    if (!res.ok) {
      const errorText = data.detail || data.error || "Something went wrong. Please try again.";
      renderMessage("error", errorText);
      return;
    }

    history.push({ role: "assistant", content: data.reply });
    saveHistory(history);
    renderMessage("assistant", data.reply);
  } catch (err) {
    renderMessage("error", "Could not reach the server. Is the backend running?");
  } finally {
    setLoading(false);
  }
}

async function clearChat() {
  const previousSessionId = sessionId;

  history = [];
  saveHistory(history);
  sessionId = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
  localStorage.setItem(STORAGE_KEY_SESSION_ID, sessionId);
  renderAll();

  try {
    await fetch(`${APP_CONFIG.API_BASE_URL}/chat/${previousSessionId}`, { method: "DELETE" });
  } catch (err) {
    // Best-effort: the old session is orphaned server-side, but the UI
    // has already moved on to a fresh session either way.
  }
}

sendBtn.addEventListener("click", sendMessage);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

inputEl.addEventListener("input", autoResizeTextarea);

clearBtn.addEventListener("click", clearChat);

renderAll();
