function wireEvents() {
    const languageSwitcher = document.getElementById("languageSwitcher");
    if (languageSwitcher) {
        languageSwitcher.addEventListener("change", (event) => {
            setLanguage(event.target.value);
        });
    }

    const carModel = document.getElementById("car_model");
    if (carModel) {
        carModel.addEventListener("change", (event) => {
            populateEngines(event.target.value);
        });
    }

    const yearMode = document.getElementById("year_mode");
    if (yearMode) {
        yearMode.addEventListener("change", updateYearModeUI);
    }

    const premiumForm = document.getElementById("premiumForm");
    if (premiumForm) {
        premiumForm.addEventListener("submit", handleCalculation);
    }

    const carPhotoInput = document.getElementById("car_photo");
    if (carPhotoInput) {
        carPhotoInput.addEventListener("change", handleCarPhotoChange);
    }

    const removeCarPhotoBtn = document.getElementById("removeCarPhotoBtn");
    if (removeCarPhotoBtn) {
        removeCarPhotoBtn.addEventListener("click", () => {
            resetCarPhotoState();
            setMessage("");
        });
    }

    const homeForm = document.getElementById("homePremiumForm");
    if (homeForm) {
        homeForm.addEventListener("submit", handleHomeCalculation);
    }

    const openAuthBtn = document.getElementById("openAuthBtn");
    if (openAuthBtn) {
        openAuthBtn.addEventListener("click", () => {
            activateAuthTab("login");
            showAuthModal();
        });
    }

    const authCloseBtn = document.getElementById("authCloseBtn");
    if (authCloseBtn) {
        authCloseBtn.addEventListener("click", closeAuthModal);
    }
    const authModal = document.getElementById("authModal");
    if (authModal) {
        authModal.addEventListener("click", (event) => {
            if (event.target.id === "authModal") {
                closeAuthModal();
            }
        });
    }

    document.querySelectorAll("[data-auth-tab]").forEach((button) => {
        button.addEventListener("click", () => activateAuthTab(button.dataset.authTab));
    });

    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", handleLogout);
    }

    const orderBtn = document.getElementById("orderBtn");
    if (orderBtn) {
        orderBtn.addEventListener("click", createOrderFromQuote);
    }
    const saveCarBtn = document.getElementById("saveCarBtn");
    if (saveCarBtn) {
        saveCarBtn.addEventListener("click", saveCurrentCar);
    }
    const pdfBtn = document.getElementById("pdfBtn");
    if (pdfBtn) {
        pdfBtn.addEventListener("click", downloadOrderPdf);
    }
    const telegramBtn = document.getElementById("telegramBtn");
    if (telegramBtn) {
        telegramBtn.addEventListener("click", sendOrderToTelegram);
    }
    const payOrderBtn = document.getElementById("payOrderBtn");
    if (payOrderBtn) {
        payOrderBtn.addEventListener("click", handlePayOrder);
    }

    const savedCarsList = document.getElementById("savedCarsList");
    if (savedCarsList) {
        savedCarsList.addEventListener("click", (event) => {
            const target = event.target;
            if (!(target instanceof HTMLElement)) {
                return;
            }
            const action = target.dataset.action;
            const id = target.dataset.id;
            if (!action || !id) {
                return;
            }

            const itemNode = target.closest("li");
            if (!itemNode) {
                return;
            }
            const savedPayload = itemNode.dataset.savedPayload ? JSON.parse(itemNode.dataset.savedPayload) : null;
            if (!savedPayload) {
                return;
            }

            if (action === "use-saved") {
                applySavedCar(savedPayload);
            } else if (action === "delete-saved") {
                deleteSavedCar(id);
            }
        });
    }

    const factorForm = document.getElementById("factorForm");
    if (factorForm) {
        factorForm.addEventListener("submit", submitFactorForm);
    }
    const telegramForm = document.getElementById("telegramForm");
    if (telegramForm) {
        telegramForm.addEventListener("submit", submitTelegramForm);
    }
    const adminModel = document.getElementById("adminModel");
    if (adminModel) {
        adminModel.addEventListener("change", async (event) => {
            try {
                const data = await requestJSON("/admin/data");
                const modelId = event.target.value;
                if (data.model_factors && data.model_factors[modelId]) {
                    const factorInput = document.getElementById("adminFactor");
                    if (factorInput) {
                        factorInput.value = data.model_factors[modelId];
                    }
                }
            } catch (error) {
                // silent
            }
        });
    }

    const adminOrdersList = document.getElementById("adminOrdersList");
    if (adminOrdersList) {
        adminOrdersList.addEventListener("click", async (event) => {
            const target = event.target;
            if (!(target instanceof HTMLElement)) {
                return;
            }
            if (target.dataset.action !== "order-status-save") {
                return;
            }
            const id = target.dataset.id;
            if (!id) {
                return;
            }

            const itemNode = target.closest("li");
            if (!itemNode) {
                return;
            }
            const select = itemNode.querySelector("select[data-action='order-status-select']");
            const status = select ? select.value : "";
            if (!status) {
                return;
            }

            target.setAttribute("disabled", "true");
            try {
                const data = await requestJSON(`/admin/orders/${id}/status`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status }),
                });
                setAdminMessage(data.message || "OK", "success");
                await loadAdminInbox();
            } catch (error) {
                setAdminMessage(error.message, "error");
            } finally {
                target.removeAttribute("disabled");
            }
        });
    }

    const adminReviewsList = document.getElementById("adminReviewsList");
    if (adminReviewsList) {
        adminReviewsList.addEventListener("click", async (event) => {
            const target = event.target;
            if (!(target instanceof HTMLElement)) {
                return;
            }
            if (target.dataset.action !== "review-status") {
                return;
            }
            const id = target.dataset.id;
            const status = target.dataset.status;
            if (!id || !status) {
                return;
            }

            target.setAttribute("disabled", "true");
            try {
                const data = await requestJSON(`/admin/reviews/${id}/status`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status }),
                });
                setAdminMessage(data.message || "OK", "success");
                await loadAdminInbox();
            } catch (error) {
                setAdminMessage(error.message, "error");
            } finally {
                target.removeAttribute("disabled");
            }
        });
    }

    const contactForm = document.getElementById("contactForm");
    if (contactForm) {
        contactForm.addEventListener("submit", handleContactSubmit);
    }
    const reviewForm = document.getElementById("reviewForm");
    if (reviewForm) {
        reviewForm.addEventListener("submit", handleReviewSubmit);
    }
}

async function loadHomeMetrics() {
    try {
        const usersElement = document.getElementById("heroMetricUsers");
        const successElement = document.getElementById("heroMetricSuccess");
        if (!usersElement && !successElement) {
            return;
        }
        const data = await requestJSON("/api/stats");
        if (usersElement && data.users) {
            usersElement.textContent = String(data.users) + "+";
        }
        if (successElement && data.success_percentage) {
            successElement.textContent = String(data.success_percentage) + "%";
        }
    } catch (error) {
    }
}

async function init() {
    const languageSwitcher = document.getElementById("languageSwitcher");
    if (languageSwitcher) {
        languageSwitcher.value = currentLanguage;
    }
    applyTranslations();
    wireEvents();
    initGoogleSignIn();
    if (document.getElementById("year_mode")) {
        updateYearModeUI();
    }
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

    const tasks = [checkAuth(), loadHomeMetrics()];
    if (document.getElementById("premiumForm") || document.getElementById("adminModel")) {
        tasks.push(loadCars());
    }
    if (document.getElementById("homePremiumForm")) {
        tasks.push(loadHomeData());
    }
    if (document.getElementById("reviewsList")) {
        tasks.push(loadReviews());
    }
    await Promise.all(tasks);
}


function bootApp() {
    init().catch((error) => {
        setMessage(error.message || "Init error", "error");
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootApp);
} else {
    bootApp();
}

