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
  localStorage.setItem("ss_emergency", user.emergency_contact || "");
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
    "ss_emergency",
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
    emergency_contact: localStorage.getItem("ss_emergency") || "",
  };
}

/** Offline SOS queue — persisted until connectivity returns */
const SOS_QUEUE_KEY = "ss_sos_queue";

function getSosQueue() {
  try {
    const raw = localStorage.getItem(SOS_QUEUE_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch (_) {
    return [];
  }
}

function setSosQueue(list) {
  localStorage.setItem(SOS_QUEUE_KEY, JSON.stringify(list || []));
}

function enqueueSos(payload) {
  const list = getSosQueue();
  list.push({
    ...payload,
    queued_at: new Date().toISOString(),
    id: `q_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
  });
  setSosQueue(list);
  return list.length;
}

async function flushSosQueue() {
  const list = getSosQueue();
  if (!list.length) return { sent: 0, left: 0 };
  const remaining = [];
  let sent = 0;
  for (const item of list) {
    try {
      const { id, queued_at, ...body } = item;
      await api("POST", "/sos", body);
      sent += 1;
    } catch (_) {
      remaining.push(item);
    }
  }
  setSosQueue(remaining);
  return { sent, left: remaining.length };
}

/** Digits only for sms:/tel: links */
function phoneDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

/** Build sms: URI (iOS uses &body=, Android uses ?body=) */
function smsHref(toNumber, body) {
  const digits = phoneDigits(toNumber);
  const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent || "");
  const sep = ios ? "&" : "?";
  const dest = digits ? digits : "";
  return `sms:${dest}${sep}body=${encodeURIComponent(body)}`;
}

function sosSmsBody(lat, lon, silent) {
  const maps = `https://maps.google.com/?q=${lat},${lon}`;
  const kind = silent ? "Silent SOS" : "SOS";
  return `Sheeghra Sahayata ${kind}: Need help. Location: ${lat.toFixed(5)}, ${lon.toFixed(5)} ${maps}`;
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
