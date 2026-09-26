(() => {
  let mode = "login";
  const phoneInput = document.getElementById("phone");

  /** Keep only digits and cap at 10. */
  function digitsOnly10(value) {
    return String(value || "").replace(/\D/g, "").slice(0, 10);
  }

  /** Store/lookup format used in DB seed: +91XXXXXXXXXX */
  function toE164India(tenDigits) {
    return `+91${tenDigits}`;
  }

  phoneInput.addEventListener("input", () => {
    phoneInput.value = digitsOnly10(phoneInput.value);
  });

  phoneInput.addEventListener("paste", (e) => {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData("text");
    phoneInput.value = digitsOnly10(text);
  });

  function applyI18n() {
    const lang = localStorage.getItem("ss_user_lang") || "en";
    const brand = document.getElementById("brand");
    if (brand) brand.textContent = t("brand");
    document.getElementById("tagline").textContent = t("tagline");
    document.getElementById("tab-login").textContent = t("login");
    document.getElementById("tab-signup").textContent = t("signup");
    document.getElementById("lbl-phone").textContent = t("phone");
    document.getElementById("lbl-otp").textContent = t("otp");
    phoneInput.placeholder = t("ph_phone");
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
    const title = document.getElementById("auth-title");
    if (title) title.textContent = mode === "signup" ? t("signup") : t("login");
  }

  document.getElementById("lang-btn").addEventListener("click", toggleLang);

  document.querySelectorAll(".seg [data-mode]").forEach((tab) => {
    tab.addEventListener("click", (e) => {
      e.preventDefault();
      mode = tab.dataset.mode;
      document.querySelectorAll(".seg [data-mode]").forEach((x) => x.classList.remove("active"));
      tab.classList.add("active");
      const signup = document.getElementById("signup-fields");
      if (signup) {
        if (mode === "signup") signup.classList.remove("hidden");
        else signup.classList.add("hidden");
      }
      applyI18n();
    });
  });

  document.getElementById("auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errEl = document.getElementById("error");
    errEl.classList.add("hidden");

    const ten = digitsOnly10(phoneInput.value);
    phoneInput.value = ten;
    if (ten.length !== 10) {
      errEl.textContent = t("phone_err");
      errEl.classList.remove("hidden");
      return;
    }

    const phone = toE164India(ten);
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
      errEl.textContent =
        err.message === "OFFLINE"
          ? "Cannot reach server — is the backend running?"
          : err.message;
      errEl.classList.remove("hidden");
    } finally {
      btn.disabled = false;
    }
  });

  applyI18n();
})();
