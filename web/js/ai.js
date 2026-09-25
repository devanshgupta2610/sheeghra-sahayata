/** Floating AI Safety Helper */

function mountAIHelper() {
  if (document.getElementById("ai-fab")) return;

  const fab = document.createElement("button");
  fab.id = "ai-fab";
  fab.className = "ai-fab";
  fab.title = "AI Helper";
  fab.textContent = "AI";
  fab.type = "button";

  const panel = document.createElement("div");
  panel.id = "ai-panel";
  panel.className = "chat-panel";
  panel.innerHTML = `
    <div class="chat-head">
      <span data-i18n="ai_title">${t("ai_title")}</span>
      <button type="button" class="btn btn-ghost" id="ai-close" style="color:#fff;padding:0.2rem 0.5rem">✕</button>
    </div>
    <div class="chat-msgs" id="ai-msgs"></div>
    <div class="chat-suggestions" id="ai-suggestions"></div>
    <form class="chat-input" id="ai-form">
      <input class="field" id="ai-input" placeholder="${t("ai_ph")}" autocomplete="off" />
      <button class="btn btn-primary" type="submit">${t("ai_send")}</button>
    </form>
  `;

  document.body.appendChild(panel);
  document.body.appendChild(fab);

  const msgs = panel.querySelector("#ai-msgs");
  const suggestions = panel.querySelector("#ai-suggestions");

  function addBubble(text, who) {
    const b = document.createElement("div");
    b.className = `bubble ${who}`;
    b.textContent = text;
    msgs.appendChild(b);
    msgs.scrollTop = msgs.scrollHeight;
  }

  addBubble(t("ai_hello"), "bot");

  function setSuggestions(list) {
    suggestions.innerHTML = "";
    (list || []).forEach((s) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.textContent = s;
      chip.addEventListener("click", () => {
        panel.querySelector("#ai-input").value = s;
        panel.querySelector("#ai-form").requestSubmit();
      });
      suggestions.appendChild(chip);
    });
  }

  setSuggestions(
    (localStorage.getItem("ss_user_lang") || "en") === "hi"
      ? ["SOS कैसे काम करता है?", "अस्पताल की मदद", "सुलभ मोड क्या है?", "आपात नंबर"]
      : ["How does SOS work?", "Nearest hospital help", "Senior accessible mode", "Emergency numbers"]
  );

  fab.addEventListener("click", () => panel.classList.toggle("open"));
  panel.querySelector("#ai-close").addEventListener("click", () => panel.classList.remove("open"));

  panel.querySelector("#ai-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = panel.querySelector("#ai-input");
    const message = input.value.trim();
    if (!message) return;
    addBubble(message, "user");
    input.value = "";
    addBubble("…", "bot");
    const thinking = msgs.lastChild;
    try {
      const s = session();
      const data = await api("POST", "/ai/chat", {
        message,
        language: s.lang || localStorage.getItem("ss_user_lang") || "en",
        user_name: s.name || null,
        age_range: s.age_range || null,
      });
      thinking.textContent = data.reply;
      if (data.suggestions) setSuggestions(data.suggestions);
    } catch (err) {
      thinking.textContent =
        err.message === "OFFLINE"
          ? "Helper offline — dial 112 in an emergency."
          : String(err.message || err);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (typeof t === "function") mountAIHelper();
});
