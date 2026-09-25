(() => {
  const s = requireAuth();
  if (!s) return;

  let lat = 28.6139;
  let lon = 77.2090;
  let tripActive = false;
  let accessible = localStorage.getItem("ss_accessible") === "1";

  const els = {
    brand: document.getElementById("brand"),
    greeting: document.getElementById("greeting"),
    langBtn: document.getElementById("lang-btn"),
    dash: document.getElementById("dash-link"),
    logout: document.getElementById("logout-btn"),
    geofence: document.getElementById("geofence"),
    tripStatus: document.getElementById("trip-status"),
    tripBtn: document.getElementById("trip-btn"),
    gpsBtn: document.getElementById("gps-btn"),
    sosBtn: document.getElementById("sos-btn"),
    silentBtn: document.getElementById("silent-btn"),
    coords: document.getElementById("coords"),
    toast: document.getElementById("toast"),
    quickTitle: document.getElementById("quick-title"),
    safetyBody: document.getElementById("safety-body"),
    offlineModal: document.getElementById("offline-modal"),
    offlineTitle: document.getElementById("offline-title"),
    offlineCoords: document.getElementById("offline-coords"),
    offlineOk: document.getElementById("offline-ok"),
  };

  function showToast(msg, ms = 3500) {
    els.toast.textContent = msg;
    els.toast.classList.remove("hidden");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => els.toast.classList.add("hidden"), ms);
  }

  function applyAccessible() {
    document.body.classList.toggle("accessible", accessible);
    localStorage.setItem("ss_accessible", accessible ? "1" : "0");
    const sw = document.getElementById("access-switch");
    if (sw) sw.classList.toggle("on", accessible);
  }

  function renderSafetyPanel() {
    const lang = s.lang || "en";
    const g = (s.gender || "").toLowerCase();
    const age = s.age_range || "";
    const isWomen = g === "female" && ["18-35", "18-25", "26-35"].includes(age);
    const isSenior = age.includes("60");

    let html = "";
    if (isWomen) {
      html = `
        <p style="font-weight:700;color:var(--coral);margin:0 0 0.5rem">${t("women")}</p>
        <a class="help-link accent" href="tel:181">📞 181</a>
        <a class="help-link" href="https://www.google.com/maps/search/police+station+near+me" target="_blank" rel="noopener">${t("police")}</a>
      `;
    } else if (isSenior) {
      html = `
        <p style="font-weight:700;color:var(--teal-deep);margin:0 0 0.35rem">${t("senior_title")}</p>
        <a class="help-link" href="https://www.google.com/maps/search/hospital+near+me" target="_blank" rel="noopener">${t("hospital")}</a>
        <a class="help-link accent" href="tel:108">${t("ambulance")}</a>
        <a class="help-link" href="tel:14567">${t("elder")}</a>
        <div class="row spread" style="margin-top:0.75rem">
          <div>
            <div style="font-weight:700">${t("accessible")}</div>
            <div class="muted" style="font-size:0.95rem">${t("accessible_hint")}</div>
          </div>
          <button type="button" class="switch ${accessible ? "on" : ""}" id="access-switch" aria-label="Accessible Mode"></button>
        </div>
      `;
    } else {
      html = `
        <p style="font-weight:700;margin:0 0 0.35rem">${t("std")}</p>
        <p class="muted" style="margin:0">112 · Police 100 · Ambulance 108 · Fire 101</p>
      `;
    }
    els.safetyBody.innerHTML = html;
    const sw = document.getElementById("access-switch");
    if (sw) {
      sw.addEventListener("click", () => {
        accessible = !accessible;
        applyAccessible();
      });
    }
  }

  function applyI18n() {
    const lang = localStorage.getItem("ss_user_lang") || "en";
    els.brand.textContent = t("brand");
    els.greeting.textContent = s.name ? `Hi, ${s.name}` : s.phone;
    els.langBtn.textContent = lang === "hi" ? "EN" : "हि";
    els.dash.textContent = t("dashboard");
    els.logout.textContent = t("logout");
    els.geofence.textContent = t("geofence");
    els.sosBtn.textContent = t("sos");
    els.silentBtn.textContent = t("silent");
    els.quickTitle.textContent = t("quick");
    els.offlineTitle.textContent = t("offline");
    updateTripUI();
    renderSafetyPanel();
  }

  function updateTripUI() {
    els.tripStatus.textContent = tripActive ? t("trip_on") : t("trip_off");
    els.tripStatus.style.color = tripActive ? "var(--ok)" : "var(--muted)";
    els.tripBtn.textContent = tripActive ? t("end_trip") : t("start_trip");
    els.tripBtn.className = tripActive ? "btn btn-amber btn-lg" : "btn btn-primary btn-lg";
    els.tripBtn.style.flex = "1";
  }

  function updateGeoUI() {
    els.coords.textContent = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    const danger = insideDangerZone(lat, lon);
    els.geofence.classList.toggle("hidden", !danger);
  }

  function getGPS() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({ lat, lon, ok: false });
        return;
      }
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
    } catch (_) { /* ignore */ }
  }

  async function startOrEndTrip() {
    els.tripBtn.disabled = true;
    try {
      if (tripActive) {
        await api("POST", "/trip/end", { trip_id: s.trip_id, user_id: s.user_id });
        tripActive = false;
        s.trip_id = "";
        localStorage.removeItem("ss_trip_id");
        showToast("Trip ended — locations will be purged (privacy)");
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
      if (err.message === "OFFLINE") showToast("Offline — try again when connected");
      else showToast(err.message);
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
      if (silent) {
        showToast(t("silent_ok"));
      } else {
        els.sosBtn.classList.add("flash");
        showToast(t("sos_ok"));
        setTimeout(() => els.sosBtn.classList.remove("flash"), 2500);
      }
    } catch (err) {
      if (err.message === "OFFLINE") {
        // Offline SMS mock — production → 112 ERSS / telecom partner SMS
        console.log(`[OFFLINE SMS MOCK] lat=${lat} lon=${lon} user=${s.user_id}`);
        els.offlineCoords.textContent = `lat=${lat}, lon=${lon}`;
        els.offlineModal.classList.remove("hidden");
      } else {
        showToast(err.message);
      }
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
    } catch (_) { /* ok */ }
    updateTripUI();
  }

  // Events
  els.langBtn.addEventListener("click", toggleLang);
  els.logout.addEventListener("click", () => {
    clearSession();
    location.href = "/";
  });
  els.tripBtn.addEventListener("click", startOrEndTrip);
  els.gpsBtn.addEventListener("click", async () => {
    await refreshGPS();
    showToast(els.coords.textContent);
  });
  els.sosBtn.addEventListener("click", () => triggerSos(false));
  els.silentBtn.addEventListener("click", () => triggerSos(true));
  els.offlineOk.addEventListener("click", () => {
    els.offlineModal.classList.add("hidden");
    showToast(t("offline_ok"));
  });

  applyAccessible();
  applyI18n();
  updateGeoUI();
  refreshGPS();
  restoreTrip();
})();
