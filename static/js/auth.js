function getGoogleClientId() {
    const config = window.APP_CONFIG || {};
    return String(config.googleClientId || "").trim();
}

function ensureGoogleAuthSection() {
    const authDialog = document.querySelector("#authModal .auth-dialog");
    const authMessage = document.getElementById("authMessage");
    if (!authDialog || !authMessage) {
        return null;
    }

    let section = document.getElementById("googleAuthSection");
    if (section) {
        const dividerText = section.querySelector(".auth-divider span");
        if (dividerText) {
            dividerText.textContent = t("auth.orGoogle");
        }
        const hint = section.querySelector(".google-auth-hint");
        if (hint) {
            hint.textContent = t("auth.googleLoading");
        }
        return section;
    }

    section = document.createElement("div");
    section.id = "googleAuthSection";
    section.className = "google-auth-section";
    section.innerHTML = `
        <div class="auth-divider"><span>${t("auth.orGoogle")}</span></div>
        <div id="googleSignInButton"></div>
        <p class="google-auth-hint">${t("auth.googleLoading")}</p>
    `;
    authDialog.insertBefore(section, authMessage);
    return section;
}

async function handleGoogleCredentialResponse(response) {
    if (!response || !response.credential) {
        setAuthMessage(t("msg.authFailed"), "error");
        return;
    }

    try {
        const data = await requestJSON("/auth/google-login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ credential: response.credential }),
        });
        updateAuthUI(data.user);
        setAuthMessage(data.message || t("msg.authSuccess"), "success");
        setTimeout(closeAuthModal, 700);
    } catch (error) {
        setAuthMessage(error.message || t("msg.authFailed"), "error");
    }
}

function initGoogleSignIn(retryCount = 0) {
    const clientId = getGoogleClientId();
    if (!clientId) {
        return;
    }

    const section = ensureGoogleAuthSection();
    const container = document.getElementById("googleSignInButton");
    if (!section || !container) {
        return;
    }

    if (!window.google || !window.google.accounts || !window.google.accounts.id) {
        if (retryCount < 20) {
            window.setTimeout(() => initGoogleSignIn(retryCount + 1), 250);
        }
        return;
    }

    const hint = section.querySelector(".google-auth-hint");
    if (!googleIdentityInitialized) {
        google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleCredentialResponse,
        });
        googleIdentityInitialized = true;
    }

    container.innerHTML = "";
    google.accounts.id.renderButton(container, {
        type: "standard",
        theme: "outline",
        size: "large",
        text: "signin_with",
        shape: "pill",
        width: 320,
        logo_alignment: "left",
    });
    if (hint) {
        hint.textContent = "";
    }
}

function showAuthModal() {
    const modal = document.getElementById("authModal");
    if (!modal) {
        return;
    }
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
    initGoogleSignIn();
}

function closeAuthModal() {
    const modal = document.getElementById("authModal");
    if (!modal) {
        return;
    }
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    setAuthMessage("");
    document.body.classList.remove("modal-open");
}

function activateAuthTab(tab) {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const buttons = document.querySelectorAll("[data-auth-tab]");

    buttons.forEach((button) => {
        button.classList.toggle("active", button.dataset.authTab === tab);
    });

    loginForm.classList.toggle("hidden", tab !== "login");
    registerForm.classList.toggle("hidden", tab !== "register");
    setAuthMessage("");
    initGoogleSignIn();
}

function updateAuthUI(user) {
    currentUser = user;
    const userBadge = document.getElementById("userBadge");
    const userName = document.getElementById("userName");
    const openAuthBtn = document.getElementById("openAuthBtn");
    const adminPanel = document.getElementById("adminPanel");
    const adminLink = document.getElementById("adminLink");

    if (adminLink) {
        adminLink.classList.toggle("hidden", !(user && user.is_admin));
    }

    if (user) {
        if (userName) {
            userName.textContent = user.name;
        }
        if (userBadge) {
            userBadge.classList.remove("hidden");
        }
        if (openAuthBtn) {
            openAuthBtn.classList.add("hidden");
        }
        if (document.getElementById("orderHistoryList") || document.getElementById("savedCarsList")) {
            refreshCabinetData();
        }
        if (adminPanel) {
            if (user.is_admin) {
                adminPanel.classList.remove("hidden");
                loadAdminData();
            } else {
                adminPanel.classList.add("hidden");
            }
        }
    } else {
        if (userBadge) {
            userBadge.classList.add("hidden");
        }
        if (openAuthBtn) {
            openAuthBtn.classList.remove("hidden");
        }
        if (adminPanel) {
            adminPanel.classList.add("hidden");
        }
        renderOrderHistory([]);
        renderSavedCars([]);
        setOrderMessage("");
    }
}

function renderOrderHistory(items) {
    const list = document.getElementById("orderHistoryList");
    if (!list) {
        return;
    }
    list.innerHTML = "";
    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = "<li class='placeholder'>Hozircha buyurtmalar yo'q.</li>";
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <div class="cabinet-item-top">
                <span class="cabinet-item-title">#${item.id} - ${item.model_name}</span>
                <span class="status-pill">${item.status}</span>
            </div>
            <div class="cabinet-item-meta">${item.year} yil, ${item.engine_cc} sm3, ${formatCurrency(item.price)}</div>
            ${item.car_photo_path ? `<img class="order-photo-thumb" src="${item.car_photo_path}" alt="Car photo">` : ""}
        `;
        list.appendChild(li);
    });
}

function renderSavedCars(items) {
    const list = document.getElementById("savedCarsList");
    if (!list) {
        return;
    }
    list.innerHTML = "";
    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = "<li class='placeholder'>Saqlangan mashinalar yo'q.</li>";
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <div class="cabinet-item-top">
                <span class="cabinet-item-title">${item.title}</span>
            </div>
            <div class="cabinet-item-meta">${item.year} yil, ${item.engine_cc} sm3</div>
            <div class="item-actions">
                <button class="mini-btn" data-action="use-saved" data-id="${item.id}">Qo'llash</button>
                <button class="mini-btn" data-action="delete-saved" data-id="${item.id}">O'chirish</button>
            </div>
        `;
        li.dataset.savedPayload = JSON.stringify(item);
        list.appendChild(li);
    });
}

function renderAdminOrders(items) {
    const list = document.getElementById("adminOrdersList");
    if (!list) {
        return;
    }
    list.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = "<li class='placeholder'>Hozircha buyurtma yo'q.</li>";
        return;
    }

    const statuses = ["submitted", "paid", "cancelled"];

    items.forEach((item) => {
        const li = document.createElement("li");

        const top = document.createElement("div");
        top.className = "cabinet-item-top";

        const title = document.createElement("span");
        title.className = "cabinet-item-title";
        title.textContent = `#${item.id} - ${item.model_name}`;

        const right = document.createElement("div");
        right.style.display = "inline-flex";
        right.style.gap = "8px";
        right.style.flexWrap = "wrap";
        right.style.justifyContent = "flex-end";

        const userPill = document.createElement("span");
        userPill.className = "pill";
        userPill.textContent = item.email || "-";

        const statusPill = document.createElement("span");
        statusPill.className = "status-pill";
        statusPill.textContent = item.status || "-";

        right.appendChild(userPill);
        right.appendChild(statusPill);

        top.appendChild(title);
        top.appendChild(right);

        const meta = document.createElement("div");
        meta.className = "cabinet-item-meta";
        meta.textContent = `${item.year} yil, ${item.engine_cc} sm3, ${formatCurrency(item.price)}`;

        const actions = document.createElement("div");
        actions.className = "item-actions";

        const select = document.createElement("select");
        select.className = "mini-select";
        select.dataset.action = "order-status-select";
        select.dataset.id = String(item.id);

        statuses.forEach((status) => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            if (status === item.status) {
                option.selected = true;
            }
            select.appendChild(option);
        });

        const saveBtn = document.createElement("button");
        saveBtn.className = "mini-btn";
        saveBtn.textContent = "Saqlash";
        saveBtn.dataset.action = "order-status-save";
        saveBtn.dataset.id = String(item.id);

        const paymentLink = document.createElement("a");
        paymentLink.className = "mini-btn";
        paymentLink.textContent = "To'lov";
        paymentLink.href = `/payment/${item.id}`;

        const pdfLink = document.createElement("a");
        pdfLink.className = "mini-btn";
        pdfLink.textContent = "PDF";
        pdfLink.href = `/orders/${item.id}/pdf`;

        actions.appendChild(select);
        actions.appendChild(saveBtn);
        actions.appendChild(paymentLink);
        actions.appendChild(pdfLink);

        li.appendChild(top);
        li.appendChild(meta);
        if (item.car_photo_path) {
            const image = document.createElement("img");
            image.className = "order-photo-thumb";
            image.src = item.car_photo_path;
            image.alt = "Car photo";
            li.appendChild(image);
        }
        li.appendChild(actions);
        list.appendChild(li);
    });
}

function renderAdminLeads(items) {
    const list = document.getElementById("adminLeadsList");
    if (!list) {
        return;
    }
    list.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = "<li class='placeholder'>Hozircha xabar yo'q.</li>";
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");

        const top = document.createElement("div");
        top.className = "cabinet-item-top";

        const title = document.createElement("span");
        title.className = "cabinet-item-title";
        title.textContent = `#${item.id} - ${item.full_name}`;

        const contact = document.createElement("span");
        contact.className = "pill";
        contact.textContent = item.contact;

        top.appendChild(title);
        top.appendChild(contact);

        const meta = document.createElement("div");
        meta.className = "cabinet-item-meta";
        meta.textContent = item.message;

        const meta2 = document.createElement("div");
        meta2.className = "cabinet-item-meta";
        meta2.textContent = `${item.created_at || ""}${item.user_email ? ` • ${item.user_email}` : ""}`;

        li.appendChild(top);
        li.appendChild(meta);
        li.appendChild(meta2);
        list.appendChild(li);
    });
}

function renderAdminReviews(items) {
    const list = document.getElementById("adminReviewsList");
    if (!list) {
        return;
    }
    list.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = "<li class='placeholder'>Hozircha review yo'q.</li>";
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");

        const top = document.createElement("div");
        top.className = "cabinet-item-top";

        const title = document.createElement("span");
        title.className = "cabinet-item-title";
        title.textContent = `#${item.id} - ${item.full_name}`;

        const right = document.createElement("div");
        right.style.display = "inline-flex";
        right.style.gap = "8px";
        right.style.flexWrap = "wrap";
        right.style.justifyContent = "flex-end";

        const rating = document.createElement("span");
        rating.className = "pill";
        rating.textContent = `${item.rating}/5`;

        const status = document.createElement("span");
        status.className = "pill";
        status.textContent = item.status;

        right.appendChild(rating);
        right.appendChild(status);

        top.appendChild(title);
        top.appendChild(right);

        const meta = document.createElement("div");
        meta.className = "cabinet-item-meta";
        meta.textContent = item.message;

        const actions = document.createElement("div");
        actions.className = "item-actions";

        const approveBtn = document.createElement("button");
        approveBtn.className = "mini-btn";
        approveBtn.textContent = "Tasdiqlash";
        approveBtn.dataset.action = "review-status";
        approveBtn.dataset.id = String(item.id);
        approveBtn.dataset.status = "approved";

        const rejectBtn = document.createElement("button");
        rejectBtn.className = "mini-btn";
        rejectBtn.textContent = "Rad etish";
        rejectBtn.dataset.action = "review-status";
        rejectBtn.dataset.id = String(item.id);
        rejectBtn.dataset.status = "rejected";

        actions.appendChild(approveBtn);
        actions.appendChild(rejectBtn);

        li.appendChild(top);
        li.appendChild(meta);
        li.appendChild(actions);
        list.appendChild(li);
    });
}

async function refreshCabinetData() {
    if (!currentUser) {
        return;
    }
    const hasOrderHistory = document.getElementById("orderHistoryList");
    const hasSavedCars = document.getElementById("savedCarsList");
    if (!hasOrderHistory && !hasSavedCars) {
        return;
    }
    try {
        const [orders, savedCars] = await Promise.all([requestJSON("/orders"), requestJSON("/saved-cars")]);
        renderOrderHistory(orders.items || []);
        renderSavedCars(savedCars.items || []);
    } catch (error) {
        setOrderMessage(error.message, "error");
    }
}

async function checkAuth() {
    try {
        const data = await requestJSON("/auth/me");
        updateAuthUI(data.authenticated ? data.user : null);
    } catch (error) {
        updateAuthUI(null);
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;

    try {
        const data = await requestJSON("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        updateAuthUI(data.user);
        setAuthMessage("msg.authSuccess", "success", true);
        setTimeout(closeAuthModal, 700);
    } catch (error) {
        setAuthMessage(error.message || t("msg.authFailed"), "error");
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const name = document.getElementById("registerName").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;

    try {
        const data = await requestJSON("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password }),
        });
        updateAuthUI(data.user);
        setAuthMessage("msg.authSuccess", "success", true);
        setTimeout(closeAuthModal, 700);
    } catch (error) {
        setAuthMessage(error.message || t("msg.authFailed"), "error");
    }
}

async function handleLogout() {
    try {
        await requestJSON("/auth/logout", { method: "POST" });
        if (window.google && window.google.accounts && window.google.accounts.id) {
            google.accounts.id.disableAutoSelect();
        }
    } finally {
        lastOrderId = null;
        const pdfBtn = document.getElementById("pdfBtn");
        const telegramBtn = document.getElementById("telegramBtn");
        if (pdfBtn) {
            pdfBtn.disabled = true;
        }
        if (telegramBtn) {
            telegramBtn.disabled = true;
        }
        const paymentLink = document.getElementById("paymentLink");
        if (paymentLink) {
            paymentLink.classList.add("hidden");
            paymentLink.setAttribute("href", "#");
        }
        updateAuthUI(null);
    }
}

async function createOrderFromQuote() {
    if (!currentUser) {
        setOrderMessage("Buyurtma berish uchun avval tizimga kiring.", "error");
        showAuthModal();
        return;
    }
    if (!lastQuotePayload) {
        setOrderMessage("Avval premiumni hisoblang.", "error");
        return;
    }

    try {
        const data = await requestJSON("/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(lastQuotePayload),
        });
        lastOrderId = data.order.id;
        document.getElementById("pdfBtn").disabled = false;
        document.getElementById("telegramBtn").disabled = false;
        const paymentLink = document.getElementById("paymentLink");
        if (paymentLink) {
            paymentLink.classList.remove("hidden");
            paymentLink.setAttribute("href", `/payment/${lastOrderId}`);
        }
        setOrderMessage(`Buyurtma #${lastOrderId} yaratildi.`, "success");
        refreshCabinetData();
    } catch (error) {
        setOrderMessage(error.message, "error");
    }
}

async function saveCurrentCar() {
    if (!currentUser) {
        setOrderMessage("Mashinani saqlash uchun avval tizimga kiring.", "error");
        showAuthModal();
        return;
    }
    if (!lastQuotePayload) {
        setOrderMessage("Avval premiumni hisoblang.", "error");
        return;
    }

    try {
        const data = await requestJSON("/saved-cars", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model_id: lastQuotePayload.model_id,
                engine: lastQuotePayload.engine,
                year: lastQuotePayload.year,
            }),
        });
        setOrderMessage(data.message || "Mashina saqlandi.", "success");
        refreshCabinetData();
    } catch (error) {
        setOrderMessage(error.message, "error");
    }
}

function downloadOrderPdf() {
    if (!lastOrderId) {
        setOrderMessage("PDF yuklash uchun avval buyurtma yarating.", "error");
        return;
    }
    window.open(`/orders/${lastOrderId}/pdf`, "_blank");
}

async function sendOrderToTelegram() {
    if (!lastOrderId) {
        setOrderMessage("Telegramga yuborish uchun avval buyurtma yarating.", "error");
        return;
    }
    try {
        const data = await requestJSON(`/orders/${lastOrderId}/send-telegram`, { method: "POST" });
        setOrderMessage(data.message || "Telegramga yuborildi.", "success");
    } catch (error) {
        setOrderMessage(error.message, "error");
    }
}

async function handlePayOrder(event) {
    const button = event.currentTarget;
    if (!(button instanceof HTMLElement)) {
        return;
    }
    const orderId = button.dataset.orderId;
    if (!orderId) {
        return;
    }

    button.setAttribute("disabled", "true");
    setInlineMessage("paymentMessage", "");

    try {
        const data = await requestJSON(`/orders/${orderId}/pay`, { method: "POST" });
        setInlineMessage("paymentMessage", data.message || "OK", "success");
        const statusEl = document.getElementById("paymentStatus");
        if (statusEl && data.status) {
            statusEl.textContent = data.status;
        }
    } catch (error) {
        setInlineMessage("paymentMessage", error.message || "Error", "error");
        if (error.status === 401) {
            activateAuthTab("login");
            showAuthModal();
        }
    } finally {
        button.removeAttribute("disabled");
    }
}

function applySavedCar(savedCar) {
    document.getElementById("car_model").value = savedCar.model_id;
    populateEngines(savedCar.model_id);
    document.getElementById("engine_select").value = String(savedCar.engine_cc);
    document.getElementById("year_mode").value = "select";
    updateYearModeUI();
    document.getElementById("year_select").value = String(savedCar.year);
    setOrderMessage("Saqlangan mashina formaga yuklandi.", "success");
}

async function deleteSavedCar(savedId) {
    try {
        await requestJSON(`/saved-cars/${savedId}`, { method: "DELETE" });
        setOrderMessage("Saqlangan mashina o'chirildi.", "success");
        refreshCabinetData();
    } catch (error) {
        setOrderMessage(error.message, "error");
    }
}

