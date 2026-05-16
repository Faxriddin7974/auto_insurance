async function loadAdminInbox() {
    if (!currentUser || !currentUser.is_admin) {
        return;
    }
    const ordersList = document.getElementById("adminOrdersList");
    const leadsList = document.getElementById("adminLeadsList");
    const reviewsList = document.getElementById("adminReviewsList");
    if (!ordersList && !leadsList && !reviewsList) {
        return;
    }

    try {
        const [orders, leads, reviews] = await Promise.all([
            requestJSON("/admin/orders"),
            requestJSON("/admin/leads"),
            requestJSON("/admin/reviews"),
        ]);
        renderAdminOrders(orders.items || []);
        renderAdminLeads(leads.items || []);
        renderAdminReviews(reviews.items || []);
    } catch (error) {
        setAdminMessage(error.message, "error");
    }
}

async function loadAdminData() {
    if (!currentUser || !currentUser.is_admin) {
        return;
    }
    try {
        const data = await requestJSON("/admin/data");
        const stats = data.stats || {};
        const statUsers = document.getElementById("adminStatUsers");
        const statOrders = document.getElementById("adminStatOrders");
        const statPaid = document.getElementById("adminStatPaid");
        const statLeads = document.getElementById("adminStatLeads");
        const statPending = document.getElementById("adminStatPending");
        if (statUsers) {
            statUsers.textContent = String(stats.users_total ?? "-");
        }
        if (statOrders) {
            statOrders.textContent = String(stats.orders_total ?? "-");
        }
        if (statPaid) {
            statPaid.textContent = String(stats.orders_paid ?? "-");
        }
        if (statLeads) {
            statLeads.textContent = String(stats.leads_total ?? "-");
        }
        if (statPending) {
            statPending.textContent = String(stats.reviews_pending ?? "-");
        }

        const modelSelect = document.getElementById("adminModel");
        if (modelSelect) {
            const previous = modelSelect.value;
            modelSelect.innerHTML = "";
            carData.forEach((car) => {
                const option = document.createElement("option");
                option.value = car.id;
                option.textContent = car.name[currentLanguage] || car.name.uz;
                modelSelect.appendChild(option);
            });
            if (previous) {
                modelSelect.value = previous;
            }

            const selectedModel = modelSelect.value;
            const factorInput = document.getElementById("adminFactor");
            if (factorInput && selectedModel && data.model_factors && data.model_factors[selectedModel]) {
                factorInput.value = data.model_factors[selectedModel];
            }
        }

        const settings = data.settings || {};
        const tokenInput = document.getElementById("tgToken");
        if (tokenInput) {
            tokenInput.value = settings.telegram_bot_token || "";
        }
        const chatInput = document.getElementById("tgChat");
        if (chatInput) {
            chatInput.value = settings.telegram_chat_id || "";
        }
        await loadAdminInbox();
    } catch (error) {
        setAdminMessage(error.message, "error");
    }
}

async function submitFactorForm(event) {
    event.preventDefault();
    try {
        const modelId = document.getElementById("adminModel").value;
        const factor = Number(document.getElementById("adminFactor").value);
        const data = await requestJSON("/admin/model-factor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_id: modelId, factor }),
        });
        setAdminMessage(data.message || "Koeffitsient saqlandi.", "success");
    } catch (error) {
        setAdminMessage(error.message, "error");
    }
}

async function submitTelegramForm(event) {
    event.preventDefault();
    try {
        const telegram_bot_token = document.getElementById("tgToken").value.trim();
        const telegram_chat_id = document.getElementById("tgChat").value.trim();
        const data = await requestJSON("/admin/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ telegram_bot_token, telegram_chat_id }),
        });
        setAdminMessage(data.message || "Sozlamalar saqlandi.", "success");
    } catch (error) {
        setAdminMessage(error.message, "error");
    }
}

