(() => {
  const s = requireAuth();
  if (!s) return;

  let lat = 28.6139;
  let lon = 77.2090;
  let tripActive = false;
  let accessible = localStorage.getItem("ss_accessible") === "1";

  const els = {
    greeting: document.getElementById("greeting"),
    langBtn: document.getElementById("lang-btn"),
    logout: document.getElementById("logout-btn"),
    geofence: document.getElementById("geofence"),
    tripBtn: document.getElementById("trip-btn"),
    gpsBtn: document.getElementById("gps-btn"),
    sosBtn: document.getElementById("sos-btn"),
    silentBtn: document.getElementById("silent-btn"),
    quickTitle: document.getElementById("quick-title"),
    safetyBody: document.getElementById("safety-body"),
    offlineModal: document.getElementById("offline-modal"),
    offlineTitle: document.getElementById("offline-title"),
    offlineCoords: document.getElementById("offline-coords"),
    offlineOk: document.getElementById("offline-ok"),
    statTrip: document.getElementById("stat-trip"),
    statCoords: document.getElementById("stat-coords"),
    statRisk: document.getElementById("stat-risk"),
    tripBadge: document.getElementById("trip-badge"),
    tripHint: document.getElementById("trip-hint"),
  };

  function showToast(msg, type = "ok") {
    if (window.toast) window.toast(msg, type);
  }

  function applyAccessible() {
    document.documentElement.style.fontSize = accessible ? "19px" : "16px";
    localStorage.setItem("ss_accessible", accessible ? "1" : "0");
    const sw = document.getElementById("access-switch");
    if (sw) sw.classList.toggle("on", accessible);
  }

  function renderSafetyPanel() {
    const g = (s.gender || "").toLowerCase();
    const age = s.age_range || "";
    const isWomen = g === "female" && ["18-35", "18-25", "26-35"].includes(age);
    const isSenior = age.includes("60");

    let html = "";
    if (isWomen) {
      html = `
        <p style="font-weight:700;color:#ff9b9b;margin:0 0 0.5rem">${t("women")}</p>
        <a class="btn btn-soft btn-block" href="tel:181">Call 181</a>
        <a class="btn btn-ghost btn-block" href="https://www.google.com/maps/search/police+station+near+me" target="_blank" rel="noopener">${t("police")}</a>
      `;
    } else if (isSenior) {
      html = `
        <p style="font-weight:700;margin:0 0 0.5rem;color:#c9d7ff">${t("senior_title")}</p>
        <a class="btn btn-ghost btn-block" href="https://www.google.com/maps/search/hospital+near+me" target="_blank" rel="noopener">${t("hospital")}</a>
        <a class="btn btn-soft btn-block" href="tel:108">${t("ambulance")}</a>
        <a class="btn btn-ghost btn-block" href="tel:14567">${t("elder")}</a>
        <div class="row spread" style="margin-top:0.75rem">
          <div>
            <div style="font-weight:650">${t("accessible")}</div>
            <div class="muted" style="font-size:0.85rem">${t("accessible_hint")}</div>
          </div>
          <button type="button" class="toggle ${accessible ? "on" : ""}" id="access-switch" aria-label="Accessible Mode"></button>
        </div>
      `;
    } else {
      html = `
        <p style="font-weight:650;margin:0 0 0.35rem">${t("std")}</p>
        <p class="muted mono" style="margin:0;font-size:0.9rem">112 · 100 · 108 · 101</p>
      `;
    }
    els.safetyBody.innerHTML = html;
    document.getElementById("access-switch")?.addEventListener("click", () => {
      accessible = !accessible;
      applyAccessible();
    });
  }

  function updateTripUI() {
    els.statTrip.textContent = tripActive ? "Active" : "Idle";
    els.tripHint.textContent = tripActive ? t("trip_on") : t("trip_off");
    els.tripBadge.textContent = tripActive ? "Sharing" : "Idle";
    els.tripBadge.className = tripActive ? "badge badge-ok" : "badge";
    els.tripBtn.textContent = tripActive ? t("end_trip") : t("start_trip");
    els.tripBtn.classList.remove("btn-primary", "btn-danger");
    els.tripBtn.classList.add(tripActive ? "btn-danger" : "btn-primary");
    els.tripBtn.style.flex = "1";
  }

  function updateGeoUI() {
    els.statCoords.textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    const danger = insideDangerZone(lat, lon);
    els.geofence.classList.toggle("hidden", !danger);
    els.geofence.textContent = t("geofence");
    els.statRisk.textContent = danger ? "High risk" : "Clear";
    els.statRisk.style.color = danger ? "var(--danger)" : "var(--ok)";
  }

  function getGPS() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) return resolve({ lat, lon, ok: false });
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude, ok: true }),
        () => resolve({ lat, lon, ok: false }),
        { enableHighAccuracy: true, timeout: 8000 }
      );
    });
  }

  async function refreshGPS() {
    const g = await getGPS();
    lat = g.lat;
    lon = g.lon;
    updateGeoUI();
  }

  async function shareLocation() {
    if (!tripActive || !s.trip_id) return;
    try {
      await api("POST", "/location", {
        user_id: s.user_id,
        trip_id: s.trip_id,
        lat,
        lon,
        timestamp: new Date().toISOString(),
      });
    } catch (_) {}
  }

  async function startOrEndTrip() {
    els.tripBtn.disabled = true;
    try {
      if (tripActive) {
        await api("POST", "/trip/end", { trip_id: s.trip_id, user_id: s.user_id });
        tripActive = false;
        s.trip_id = "";
        localStorage.removeItem("ss_trip_id");
        showToast("Trip ended — locations will be purged");
      } else {
        const data = await api("POST", "/trip/start", { user_id: s.user_id });
        tripActive = true;
        s.trip_id = data.trip.id;
        localStorage.setItem("ss_trip_id", s.trip_id);
        await refreshGPS();
        await shareLocation();
        showToast("Trip started");
      }
      updateTripUI();
    } catch (err) {
      showToast(err.message === "OFFLINE" ? "Offline" : err.message, "err");
    } finally {
      els.tripBtn.disabled = false;
    }
  }

  async function triggerSos(silent) {
    await refreshGPS();
    try {
      await api("POST", "/sos", {
        user_id: s.user_id,
        trip_id: s.trip_id || null,
        lat,
        lon,
        timestamp: new Date().toISOString(),
        silent: !!silent,
      });
      if (silent) showToast(t("silent_ok"));
      else {
        els.sosBtn.classList.add("flash");
        showToast(t("sos_ok"));
        setTimeout(() => els.sosBtn.classList.remove("flash"), 2500);
      }
    } catch (err) {
      if (err.message === "OFFLINE") {
        console.log(`[OFFLINE SMS MOCK] lat=${lat} lon=${lon} user=${s.user_id}`);
        els.offlineCoords.textContent = `lat=${lat}, lon=${lon}`;
        els.offlineModal.classList.add("open");
      } else showToast(err.message, "err");
    }
  }

  async function restoreTrip() {
    try {
      const data = await api("GET", `/trip/active/${s.user_id}`);
      if (data.trip) {
        tripActive = true;
        s.trip_id = data.trip.id;
        localStorage.setItem("ss_trip_id", s.trip_id);
      }
    } catch (_) {}
    updateTripUI();
  }

  function applyI18n() {
    const lang = localStorage.getItem("ss_user_lang") || "en";
    els.greeting.textContent = s.name ? `Hi, ${s.name}` : s.phone;
    if (els.langBtn) els.langBtn.textContent = lang === "hi" ? "Language · EN" : "Language · हि";
    if (els.logout) els.logout.textContent = t("logout");
    els.sosBtn.textContent = t("sos");
    els.silentBtn.textContent = t("silent");
    els.quickTitle.textContent = t("quick");
    els.offlineTitle.textContent = t("offline");
    updateTripUI();
    renderSafetyPanel();
  }

  els.langBtn?.addEventListener("click", toggleLang);
  els.logout?.addEventListener("click", () => {
    clearSession();
    location.href = "/login";
  });
  els.tripBtn.addEventListener("click", startOrEndTrip);
  els.gpsBtn.addEventListener("click", async () => {
    await refreshGPS();
    showToast(els.statCoords.textContent);
  });
  els.sosBtn.addEventListener("click", () => triggerSos(false));
  els.silentBtn.addEventListener("click", () => triggerSos(true));
  document.getElementById("tab-sos")?.addEventListener("click", (e) => {
    e.preventDefault();
    triggerSos(false);
  });
  document.getElementById("tab-ai")?.addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("ai-fab")?.click();
  });
  document.getElementById("tab-out")?.addEventListener("click", (e) => {
    e.preventDefault();
    clearSession();
    location.href = "/login";
  });
  els.offlineOk.addEventListener("click", () => {
    els.offlineModal.classList.remove("open");
    showToast(t("offline_ok"));
  });

  applyAccessible();
  applyI18n();
  updateGeoUI();
  refreshGPS();
  restoreTrip();
})();
