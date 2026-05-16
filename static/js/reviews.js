function renderReviews(items) {
    const container = document.getElementById("reviewsList");
    if (!container) {
        return;
    }
    container.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const placeholder = document.createElement("p");
        placeholder.className = "placeholder";
        placeholder.textContent = t("reviews.empty");
        container.appendChild(placeholder);
        return;
    }

    items.forEach((item) => {
        const card = document.createElement("article");
        card.className = "review-card";

        const head = document.createElement("div");
        head.className = "review-head";

        const authorWrap = document.createElement("div");
        authorWrap.className = "review-author";

        const author = document.createElement("strong");
        author.textContent = item.author || "-";

        const meta = document.createElement("span");
        const date = item.created_at ? new Date(item.created_at) : null;
        const dateText = date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString(localeByLang[currentLanguage] || "uz-UZ") : "";
        meta.textContent = `${item.rating || "-"}\/5${dateText ? ` • ${dateText}` : ""}`;

        authorWrap.appendChild(author);
        authorWrap.appendChild(meta);

        const pills = document.createElement("div");
        const ratingPill = document.createElement("span");
        ratingPill.className = "pill";
        ratingPill.textContent = `${item.rating || "-"}\/5`;
        pills.appendChild(ratingPill);

        if (item.status && item.status !== "approved") {
            const statusPill = document.createElement("span");
            statusPill.className = "pill";
            statusPill.textContent = t(`reviews.status.${item.status}`);
            pills.appendChild(statusPill);
        }

        head.appendChild(authorWrap);
        head.appendChild(pills);

        const message = document.createElement("p");
        message.className = "review-message";
        message.textContent = item.message || "";

        card.appendChild(head);
        card.appendChild(message);
        container.appendChild(card);
    });
}

async function loadReviews() {
    const container = document.getElementById("reviewsList");
    if (!container) {
        return;
    }
    container.innerHTML = "";
    const placeholder = document.createElement("p");
    placeholder.className = "placeholder";
    placeholder.textContent = t("reviews.loading");
    container.appendChild(placeholder);

    try {
        const data = await requestJSON("/api/reviews");
        renderReviews(data.items || []);
    } catch (error) {
        container.innerHTML = "";
        const message = document.createElement("p");
        message.className = "placeholder";
        message.textContent = error.message || "Request failed";
        container.appendChild(message);
    }
}

async function handleReviewSubmit(event) {
    event.preventDefault();
    const ratingInput = document.getElementById("reviewRating");
    const textInput = document.getElementById("reviewText");
    if (!ratingInput || !textInput) {
        return;
    }
    const payload = {
        rating: Number(ratingInput.value),
        message: String(textInput.value || "").trim(),
    };

    if (!payload.message || payload.message.length < 10) {
        setInlineMessage("reviewMessage", "Fikr kamida 10 ta belgidan iborat bo'lishi kerak.", "error");
        return;
    }

    const submitBtn = event.target.querySelector("button[type='submit']");
    if (submitBtn) {
        submitBtn.disabled = true;
    }
    setInlineMessage("reviewMessage", "");

    try {
        const data = await requestJSON("/api/reviews", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        setInlineMessage("reviewMessage", data.message || t("msg.authSuccess"), "success");
        textInput.value = "";
        await loadReviews();
    } catch (error) {
        setInlineMessage("reviewMessage", error.message || "Error", "error");
        if (error.status === 401) {
            activateAuthTab("login");
            showAuthModal();
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }
}

async function handleContactSubmit(event) {
    event.preventDefault();
    const nameInput = document.getElementById("contactName");
    const contactInput = document.getElementById("contactInfo");
    const messageInput = document.getElementById("contactText");
    if (!nameInput || !contactInput || !messageInput) {
        return;
    }

    const payload = {
        name: String(nameInput.value || "").trim(),
        contact: String(contactInput.value || "").trim(),
        message: String(messageInput.value || "").trim(),
    };

    const submitBtn = event.target.querySelector("button[type='submit']");
    if (submitBtn) {
        submitBtn.disabled = true;
    }
    setInlineMessage("contactMessage", "");

    try {
        const data = await requestJSON("/api/contact", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        setInlineMessage("contactMessage", data.message || t("msg.authSuccess"), "success");
        nameInput.value = "";
        contactInput.value = "";
        messageInput.value = "";
    } catch (error) {
        setInlineMessage("contactMessage", error.message || "Error", "error");
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }
}

