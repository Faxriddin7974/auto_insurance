function t(key) {
    const langPack = TRANSLATIONS[currentLanguage] || {};
    if (Object.prototype.hasOwnProperty.call(langPack, key)) {
        return langPack[key];
    }
    if (Object.prototype.hasOwnProperty.call(TRANSLATIONS.uz, key)) {
        return TRANSLATIONS.uz[key];
    }
    return key;
}

function formatCurrency(value) {
    const locale = localeByLang[currentLanguage] || "uz-UZ";
    return `${Number(value || 0).toLocaleString(locale)} UZS`;
}

function applyTranslations() {
    document.documentElement.lang = currentLanguage;

    document.querySelectorAll("[data-i18n]").forEach((element) => {
        const key = element.getAttribute("data-i18n");
        element.textContent = t(key);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
        const key = element.getAttribute("data-i18n-placeholder");
        element.setAttribute("placeholder", t(key));
    });

    if (lastBreakdown.length > 0) {
        renderBreakdown(lastBreakdown);
        renderChart(lastBreakdown);
    }
}

function setLanguage(lang) {
    if (!TRANSLATIONS[lang]) {
        return;
    }

    currentLanguage = lang;
    try {
        if (window.localStorage) {
            window.localStorage.setItem("app_lang", lang);
        }
    } catch (error) {
        // Ignore storage errors and keep the selected language in-memory.
    }
    applyTranslations();
    if (document.getElementById("car_model")) {
        populateCarModels();
    }
    if (document.getElementById("home_type")) {
        populateHomeSelects();
    }
    if (document.getElementById("reviewsList")) {
        loadReviews();
    }
    initGoogleSignIn();
}

function setMessage(message, type = "", translateKey = false) {
    const formMessage = document.getElementById("formMessage");
    if (!formMessage) {
        return;
    }
    formMessage.textContent = translateKey ? t(message) : message;
    formMessage.classList.remove("error", "success");
    if (type) {
        formMessage.classList.add(type);
    }
}

function setOrderMessage(message, type = "") {
    const element = document.getElementById("orderMessage");
    if (!element) {
        return;
    }
    element.textContent = message;
    element.classList.remove("error", "success");
    if (type) {
        element.classList.add(type);
    }
}

function resetCarPhotoState() {
    lastCarPhoto = null;
    const input = document.getElementById("car_photo");
    const preview = document.getElementById("carPhotoPreview");
    const image = document.getElementById("carPhotoPreviewImage");
    const name = document.getElementById("carPhotoName");
    const status = document.getElementById("carPhotoStatus");

    if (input) {
        input.value = "";
    }
    if (preview) {
        preview.classList.add("hidden");
    }
    if (image) {
        image.removeAttribute("src");
    }
    if (name) {
        name.textContent = "-";
    }
    if (status) {
        status.textContent = "";
    }
}

function showCarPhotoPreview(file, statusMessage = "") {
    const preview = document.getElementById("carPhotoPreview");
    const image = document.getElementById("carPhotoPreviewImage");
    const name = document.getElementById("carPhotoName");
    const status = document.getElementById("carPhotoStatus");
    if (!preview || !image || !name || !status || !file) {
        return;
    }

    preview.classList.remove("hidden");
    image.src = URL.createObjectURL(file);
    image.onload = () => {
        URL.revokeObjectURL(image.src);
    };
    name.textContent = file.name;
    status.textContent = statusMessage;
}

async function uploadCarPhoto(file) {
    const formData = new FormData();
    formData.append("photo", file);

    const response = await fetch("/api/car-photo", {
        method: "POST",
        body: formData,
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const error = new Error(data.error || `Request failed: ${response.status}`);
        error.status = response.status;
        throw error;
    }

    return data;
}

async function handleCarPhotoChange(event) {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || !input.files || !input.files[0]) {
        resetCarPhotoState();
        return;
    }

    const file = input.files[0];
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
        resetCarPhotoState();
        setMessage("msg.photoType", "error", true);
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        resetCarPhotoState();
        setMessage("msg.photoSize", "error", true);
        return;
    }

    showCarPhotoPreview(file, t("msg.uploadingPhoto"));
    setMessage("msg.uploadingPhoto", "", true);

    try {
        const data = await uploadCarPhoto(file);
        lastCarPhoto = {
            path: data.photo_path,
            name: file.name,
        };
        showCarPhotoPreview(file, t("msg.photoReady"));
        setMessage("msg.photoReady", "success", true);
    } catch (error) {
        resetCarPhotoState();
        setMessage(error.message, "error");
    }
}

function setAdminMessage(message, type = "") {
    const element = document.getElementById("adminMessage");
    if (!element) {
        return;
    }
    element.textContent = message;
    element.classList.remove("error", "success");
    if (type) {
        element.classList.add(type);
    }
}

function setAuthMessage(message, type = "", translateKey = false) {
    const authMessage = document.getElementById("authMessage");
    if (!authMessage) {
        return;
    }
    authMessage.textContent = translateKey ? t(message) : message;
    authMessage.classList.remove("error", "success");
    if (type) {
        authMessage.classList.add(type);
    }
}


async function requestJSON(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const error = new Error(data.error || `Request failed: ${response.status}`);
        error.status = response.status;
        error.data = data;
        throw error;
    }

    return data;
}

function setInlineMessage(elementId, message, type = "") {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.textContent = message;
    element.classList.remove("error", "success");
    if (type) {
        element.classList.add(type);
    }
}

