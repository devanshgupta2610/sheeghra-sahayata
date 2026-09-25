/** API base — same origin on Railway; Vercel points at Railway API */
window.SHEEGHRA_API =
  new URLSearchParams(location.search).get("api") ||
  localStorage.getItem("ss_api") ||
  (location.hostname.endsWith("vercel.app")
    ? "https://sheeghra-sahayata-production.up.railway.app"
    : location.port === "8000" || location.port === ""
      ? ""
      : "http://127.0.0.1:8000");

async function api(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  let res;
  try {
    res = await fetch(`${window.SHEEGHRA_API}${path}`, opts);
  } catch (e) {
    const err = new Error("OFFLINE");
    err.cause = e;
    throw err;
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.detail || res.statusText || "Request failed");
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function saveSession(user) {
  localStorage.setItem("ss_user_id", user.id);
  localStorage.setItem("ss_user_name", user.name || "");
  localStorage.setItem("ss_user_phone", user.phone || "");
  localStorage.setItem("ss_user_gender", user.gender || "");
  localStorage.setItem("ss_user_age", user.age_range || "");
  localStorage.setItem("ss_user_lang", user.language_pref || "en");
}

function clearSession() {
  [
    "ss_user_id",
    "ss_user_name",
    "ss_user_phone",
    "ss_user_gender",
    "ss_user_age",
    "ss_user_lang",
    "ss_trip_id",
  ].forEach((k) => localStorage.removeItem(k));
}

function session() {
  return {
    user_id: localStorage.getItem("ss_user_id") || "",
    name: localStorage.getItem("ss_user_name") || "",
    phone: localStorage.getItem("ss_user_phone") || "",
    gender: localStorage.getItem("ss_user_gender") || "",
    age_range: localStorage.getItem("ss_user_age") || "",
    lang: localStorage.getItem("ss_user_lang") || "en",
    trip_id: localStorage.getItem("ss_trip_id") || "",
  };
}

function requireAuth() {
  const s = session();
  if (!s.user_id) {
    location.href = "/login";
    return null;
  }
  return s;
}

/** Haversine distance (metres) */
function haversineM(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

window.DANGER_ZONE = { name: "Connaught Place High-Risk Demo Zone", lat: 28.6315, lon: 77.2167, radius_m: 800 };

function insideDangerZone(lat, lon) {
  return haversineM(lat, lon, DANGER_ZONE.lat, DANGER_ZONE.lon) <= DANGER_ZONE.radius_m;
}
