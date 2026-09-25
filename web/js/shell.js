/** App shell — sidebar drawer, ⌘K search, toasts */

function toast(message, type = "ok") {
  const wrap = document.getElementById("toast-wrap");
  if (!wrap) return;
  const el = document.createElement("div");
  el.className = `toast glass ${type === "err" ? "toast-err" : "toast-ok"}`;
  el.textContent = message;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function initShell() {
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("drawer-backdrop");
  const hamburger = document.getElementById("hamburger");

  function closeDrawer() {
    sidebar?.classList.remove("open");
    if (backdrop) {
      backdrop.hidden = true;
      backdrop.classList.remove("open");
    }
  }
  function openDrawer() {
    sidebar?.classList.add("open");
    if (backdrop) {
      backdrop.hidden = false;
      backdrop.classList.add("open");
    }
  }

  hamburger?.addEventListener("click", openDrawer);
  backdrop?.addEventListener("click", closeDrawer);

  const search = document.getElementById("search-pill");
  search?.addEventListener("click", () => {
    const q = prompt("Search helplines or tips:", "Ambulance 108");
    if (q) toast(`Showing guidance for “${q}”`);
  });

  document.getElementById("notif-btn")?.addEventListener("click", () => {
    toast("No new alerts. Active SOS appears on the authority map.");
  });

  document.getElementById("user-avatar")?.addEventListener("click", () => {
    const s = typeof session === "function" ? session() : {};
    toast(s.name || s.phone || "Tourist profile");
  });

  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      search?.click();
    }
  });

  // Avatar initials
  const av = document.getElementById("user-avatar");
  if (av && typeof session === "function") {
    const s = session();
    const n = (s.name || s.phone || "T").trim();
    av.textContent = n.charAt(0).toUpperCase();
  }
}

function animateCount(el, to, ms = 700) {
  if (!el) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) {
    el.textContent = String(to);
    return;
  }
  const start = performance.now();
  const from = 0;
  function frame(t) {
    const p = Math.min(1, (t - start) / ms);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = String(Math.round(from + (to - from) * eased));
    if (p < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

document.addEventListener("DOMContentLoaded", initShell);

window.toast = toast;
window.animateCount = animateCount;
