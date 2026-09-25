(() => {
  const listEl = document.getElementById("list");
  const msgEl = document.getElementById("msg");
  const map = L.map("map").setView([28.6139, 77.209], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 19,
  }).addTo(map);

  let layer = L.layerGroup().addTo(map);

  function showMsg(text) {
    msgEl.textContent = text;
    msgEl.classList.remove("hidden");
    setTimeout(() => msgEl.classList.add("hidden"), 2500);
  }

  function colorFor(status) {
    if (status === "resolved") return "gray";
    if (status === "acknowledged") return "orange";
    return "#c75b4a";
  }

  function renderMap(incidents) {
    layer.clearLayers();
    incidents.forEach((inc) => {
      const icon = L.divIcon({
        className: "",
        html: `<div style="background:${colorFor(inc.status)};width:16px;height:16px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      });
      L.marker([inc.lat, inc.lon], { icon })
        .addTo(layer)
        .bindPopup(`<b>${(inc.type || "sos").toUpperCase()}</b> · ${inc.status}<br/>#${String(inc.id).slice(0, 8)}`);
    });
    if (incidents.length) {
      map.setView([incidents[0].lat, incidents[0].lon], 11);
    }
    setTimeout(() => map.invalidateSize(), 200);
  }

  async function setStatus(id, status) {
    try {
      await api("PATCH", `/incidents/${id}`, { status });
      showMsg(`Marked ${status}`);
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
        const ack =
          inc.status === "active"
            ? `<button type="button" class="btn btn-amber" data-ack="${inc.id}">Acknowledge</button>`
            : "";
        const res =
          inc.status === "active" || inc.status === "acknowledged"
            ? `<button type="button" class="btn btn-primary" data-res="${inc.id}" style="background:var(--ok)">Resolve</button>`
            : "";
        return `
          <div class="incident">
            <div>
              <div class="row" style="gap:0.5rem;margin-bottom:0.35rem">
                <strong style="text-transform:uppercase">${inc.type || "sos"}</strong>
                <span class="badge ${inc.status}">${inc.status}</span>
              </div>
              <div class="muted" style="font-size:0.95rem">${inc.lat}, ${inc.lon}</div>
              <div class="muted" style="font-size:0.9rem">${when}</div>
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

  async function load() {
    try {
      const data = await api("GET", "/incidents");
      const incidents = data.incidents || [];
      renderMap(incidents);
      renderList(incidents);
      document.getElementById("live-badge").textContent = "● LIVE";
    } catch (err) {
      document.getElementById("live-badge").textContent = "○ OFFLINE";
      showMsg(err.message === "OFFLINE" ? "Cannot reach API" : err.message);
    }
  }

  document.getElementById("refresh-btn").addEventListener("click", load);
  load();
  setInterval(load, 5000);
})();
