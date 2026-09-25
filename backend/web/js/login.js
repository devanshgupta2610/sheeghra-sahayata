(() => {
  let mode = "login";

  function applyI18n() {
    const lang = localStorage.getItem("ss_user_lang") || "en";
    document.getElementById("brand").textContent = t("brand");
    document.getElementById("tagline").textContent = t("tagline");
    document.getElementById("tab-login").textContent = t("login");
    document.getElementById("tab-signup").textContent = t("signup");
    document.getElementById("lbl-phone").textContent = t("phone");
    document.getElementById("lbl-otp").textContent = t("otp");
    document.getElementById("phone").placeholder = t("ph_phone");
    document.getElementById("otp").placeholder = t("ph_otp");
    document.getElementById("lbl-name").textContent = t("name");
    document.getElementById("lbl-emergency").textContent = t("emergency");
    document.getElementById("lbl-blood").textContent = t("blood");
    document.getElementById("lbl-allergies").textContent = t("allergies");
    document.getElementById("lbl-age").textContent = t("age");
    document.getElementById("lbl-gender").textContent = t("gender");
    document.getElementById("dash-link").textContent = t("dashboard");
    document.getElementById("lang-btn").textContent = lang === "hi" ? "EN" : "हि";
    document.getElementById("submit-btn").textContent = mode === "signup" ? t("signup") : t("login");
  }

  document.getElementById("lang-btn").addEventListener("click", toggleLang);

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      mode = tab.dataset.mode;
      document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById("signup-fields").classList.toggle("hidden", mode !== "signup");
      applyI18n();
    });
  });

  document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errEl = document.getElementById("error");
    errEl.classList.add("hidden");
    const phone = document.getElementById("phone").value.trim();
    const otp = document.getElementById("otp").value.trim();
    const btn = document.getElementById("submit-btn");
    btn.disabled = true;

    try {
      let data;
      if (mode === "signup") {
        data = await api("POST", "/auth/signup", {
          phone,
          otp,
          name: document.getElementById("name").value.trim() || null,
          emergency_contact: document.getElementById("emergency").value.trim() || null,
          medical_info: {
            blood_group: document.getElementById("blood").value.trim(),
            allergies: document.getElementById("allergies").value.trim(),
          },
          language_pref: localStorage.getItem("ss_user_lang") || "en",
          age_range: document.getElementById("age").value || null,
          gender: document.getElementById("gender").value || null,
        });
      } else {
        data = await api("POST", "/auth/login", { phone, otp });
      }
      saveSession(data.user);
      location.href = "/home";
    } catch (err) {
      errEl.textContent = err.message === "OFFLINE" ? "Cannot reach server — is the backend running?" : err.message;
      errEl.classList.remove("hidden");
    } finally {
      btn.disabled = false;
    }
  });

  // Already logged in?
  if (localStorage.getItem("ss_user_id")) {
    // stay on login so user can switch accounts; optional auto-redirect:
    // location.href = "/home";
  }

  applyI18n();
})();
