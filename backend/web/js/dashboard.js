(() => {
  const listEl = document.getElementById("list");
  const msgEl = document.getElementById("msg");
  const map = L.map("map").setView([28.6139, 77.209], 11);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; CARTO",
    maxZoom: 19,
  }).addTo(map);

  let layer = L.layerGroup().addTo(map);

  function showMsg(text) {
    msgEl.textContent = text;
    msgEl.classList.remove("hidden");
    setTimeout(() => msgEl.classList.add("hidden"), 2500);
  }

  function colorFor(status) {
    if (status === "resolved") return "#5c6578";
    if (status === "acknowledged") return "#f0b429";
    return "#ff5c5c";
  }

  function renderMap(incidents) {
    layer.clearLayers();
    incidents.forEach((inc) => {
      const icon = L.divIcon({
        className: "",
        html: `<div style="background:${colorFor(inc.status)};width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 12px ${colorFor(inc.status)}"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });
      L.marker([inc.lat, inc.lon], { icon })
        .addTo(layer)
        .bindPopup(`<b>${(inc.type || "sos").toUpperCase()}</b> · ${inc.status}`);
    });
    if (incidents.length) map.setView([incidents[0].lat, incidents[0].lon], 11);
    setTimeout(() => map.invalidateSize(), 200);
  }

  async function setStatus(id, status) {
    try {
      await api("PATCH", `/incidents/${id}`, { status });
      if (window.toast) window.toast(`Marked ${status}`);
      await load();
    } catch (err) {
      showMsg(err.message);
    }
  }

  function renderList(incidents) {
    if (!incidents.length) {
      listEl.innerHTML = `<p class="muted">No incidents yet.</p>`;
      return;
    }
    listEl.innerHTML = incidents
      .map((inc) => {
        const when = String(inc.created_at || "").replace(/"/g, "");
        const badge =
          inc.status === "active"
            ? "badge-danger"
            : inc.status === "acknowledged"
              ? "badge-warn"
              : "badge-ok";
        const ack =
          inc.status === "active"
            ? `<button type="button" class="btn btn-soft" data-ack="${inc.id}">Acknowledge</button>`
            : "";
        const res =
          inc.status === "active" || inc.status === "acknowledged"
            ? `<button type="button" class="btn btn-ghost" data-res="${inc.id}">Resolve</button>`
            : "";
        return `
          <div class="glass incident">
            <div>
              <div class="row" style="margin-bottom:0.4rem;flex-wrap:wrap">
                <strong style="text-transform:uppercase;letter-spacing:0.04em">${inc.type || "sos"}</strong>
                <span class="badge ${badge}">${inc.status}</span>
              </div>
              <div class="mono muted" style="font-size:0.85rem">${inc.lat}, ${inc.lon}</div>
              <div class="muted" style="font-size:0.8rem;margin-top:0.25rem">${when}</div>
            </div>
            <div class="stack" style="gap:0.4rem">${ack}${res}</div>
          </div>`;
      })
      .join("");

    listEl.querySelectorAll("[data-ack]").forEach((btn) => {
      btn.addEventListener("click", () => setStatus(btn.dataset.ack, "acknowledged"));
    });
    listEl.querySelectorAll("[data-res]").forEach((btn) => {
      btn.addEventListener("click", () => setStatus(btn.dataset.res, "resolved"));
    });
  }

  function updateStats(incidents) {
    const active = incidents.filter((i) => i.status === "active").length;
    const ack = incidents.filter((i) => i.status === "acknowledged").length;
    const res = incidents.filter((i) => i.status === "resolved").length;
    if (window.animateCount) {
      window.animateCount(document.getElementById("stat-active"), active);
      window.animateCount(document.getElementById("stat-ack"), ack);
      window.animateCount(document.getElementById("stat-res"), res);
    } else {
      document.getElementById("stat-active").textContent = active;
      document.getElementById("stat-ack").textContent = ack;
      document.getElementById("stat-res").textContent = res;
    }
  }

  async function load() {
    try {
      const data = await api("GET", "/incidents");
      const incidents = data.incidents || [];
      renderMap(incidents);
      renderList(incidents);
      updateStats(incidents);
      document.getElementById("live-badge").textContent = "Live";
      document.getElementById("live-badge").className = "badge badge-ok";
    } catch (err) {
      document.getElementById("live-badge").textContent = "Offline";
      document.getElementById("live-badge").className = "badge badge-danger";
      showMsg(err.message === "OFFLINE" ? "Cannot reach API" : err.message);
    }
  }

  document.getElementById("refresh-btn").addEventListener("click", load);
  load();
  setInterval(load, 5000);
})();
