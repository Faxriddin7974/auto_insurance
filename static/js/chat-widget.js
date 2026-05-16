(() => {
    const STORAGE_KEY = "avtosugurta_chat_history_v1";

    const uiText = {
        title: "Yordamchi",
        subtitle: "Sug'urta bo'yicha savol bering",
        placeholder: "Savolingizni yozing...",
        send: "Yuborish",
        typing: "Yozilyapti...",
        errorGeneric: "Xatolik yuz berdi. Qayta urinib ko'ring.",
    };

    function safeJsonParse(value, fallback) {
        try {
            return JSON.parse(value);
        } catch (e) {
            return fallback;
        }
    }

    function loadHistory() {
        try {
            if (!window.localStorage) {
                return [];
            }
            const raw = window.localStorage.getItem(STORAGE_KEY) || "";
            const parsed = safeJsonParse(raw, []);
            return Array.isArray(parsed) ? parsed : [];
        } catch (e) {
            return [];
        }
    }

    function saveHistory(items) {
        try {
            if (!window.localStorage) {
                return;
            }
            const trimmed = Array.isArray(items) ? items.slice(-50) : [];
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
        } catch (e) {
            // ignore
        }
    }

    function scrollToBottom(container) {
        if (!container) {
            return;
        }
        container.scrollTop = container.scrollHeight;
    }

    function createMessage(messagesEl, role, text) {
        const row = document.createElement("div");
        row.className = `chat-row chat-${role}`;

        const bubble = document.createElement("div");
        bubble.className = "chat-bubble";
        bubble.textContent = text;
        row.appendChild(bubble);

        messagesEl.appendChild(row);
        scrollToBottom(messagesEl);
        return bubble;
    }

    function setOpen(root, open) {
        if (!root) {
            return;
        }
        root.classList.toggle("chat-open", Boolean(open));
        const panel = root.querySelector(".chat-panel");
        const fab = root.querySelector(".chat-fab");
        if (panel instanceof HTMLElement) {
            panel.setAttribute("aria-hidden", open ? "false" : "true");
        }
        if (fab instanceof HTMLElement) {
            fab.setAttribute("aria-expanded", open ? "true" : "false");
        }
    }

    async function typeText(target, text, speedMs = 14) {
        if (!target) {
            return;
        }
        target.textContent = "";
        const chars = Array.from(String(text || ""));
        for (let i = 0; i < chars.length; i++) {
            target.textContent += chars[i];
            // Keep it snappy for short Uzbek answers.
            // eslint-disable-next-line no-await-in-loop
            await new Promise((resolve) => setTimeout(resolve, speedMs));
        }
    }

    async function sendChatMessage({ inputEl, sendBtn, messagesEl, history }) {
        const text = String(inputEl.value || "").trim();
        if (!text) {
            return;
        }

        inputEl.value = "";
        inputEl.focus();

        createMessage(messagesEl, "user", text);
        history.push({ role: "user", text });
        saveHistory(history);

        const typingBubble = createMessage(messagesEl, "bot", uiText.typing);
        typingBubble.classList.add("chat-typing");

        sendBtn.setAttribute("disabled", "true");
        inputEl.setAttribute("disabled", "true");

        try {
            const resp = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
            });

            const data = await resp.json().catch(() => ({}));
            if (!resp.ok) {
                const msg = String(data.error || uiText.errorGeneric);
                typingBubble.classList.remove("chat-typing");
                typingBubble.textContent = msg;
                history.push({ role: "bot", text: msg });
                saveHistory(history);
                return;
            }

            const reply = String(data.reply || "").trim();
            const finalText = reply || uiText.errorGeneric;
            typingBubble.classList.remove("chat-typing");
            await typeText(typingBubble, finalText, 12);

            history.push({ role: "bot", text: finalText });
            saveHistory(history);
        } catch (err) {
            const msg = uiText.errorGeneric;
            typingBubble.classList.remove("chat-typing");
            typingBubble.textContent = msg;
            history.push({ role: "bot", text: msg });
            saveHistory(history);
        } finally {
            sendBtn.removeAttribute("disabled");
            inputEl.removeAttribute("disabled");
        }
    }

    function buildWidget() {
        if (document.getElementById("chatWidget")) {
            return;
        }

        const root = document.createElement("div");
        root.id = "chatWidget";
        root.className = "chat-widget";

        root.innerHTML = `
            <button type="button" class="chat-fab" aria-expanded="false" aria-controls="chatPanel">
                <span class="chat-fab-dot" aria-hidden="true"></span>
                <span class="chat-fab-text">${uiText.title}</span>
            </button>

            <section class="chat-panel card" id="chatPanel" aria-hidden="true" role="dialog" aria-label="${uiText.title}">
                <header class="chat-head">
                    <div class="chat-head-text">
                        <strong>${uiText.title}</strong>
                        <span>${uiText.subtitle}</span>
                    </div>
                    <button type="button" class="chat-close" aria-label="Close">×</button>
                </header>

                <div class="chat-messages" aria-live="polite" aria-relevant="additions text"></div>

                <form class="chat-input" autocomplete="off">
                    <textarea rows="1" class="chat-textarea" placeholder="${uiText.placeholder}" aria-label="Message"></textarea>
                    <button type="submit" class="chat-send">${uiText.send}</button>
                </form>
            </section>
        `;

        document.body.appendChild(root);

        const fab = root.querySelector(".chat-fab");
        const panel = root.querySelector(".chat-panel");
        const closeBtn = root.querySelector(".chat-close");
        const messagesEl = root.querySelector(".chat-messages");
        const form = root.querySelector(".chat-input");
        const inputEl = root.querySelector(".chat-textarea");
        const sendBtn = root.querySelector(".chat-send");

        if (!(messagesEl instanceof HTMLElement) || !(form instanceof HTMLFormElement)) {
            return;
        }
        if (!(inputEl instanceof HTMLTextAreaElement) || !(sendBtn instanceof HTMLButtonElement)) {
            return;
        }

        const history = loadHistory();
        history.forEach((item) => {
            const role = item && item.role === "user" ? "user" : "bot";
            const text = String(item && item.text ? item.text : "").trim();
            if (text) {
                createMessage(messagesEl, role, text);
            }
        });

        const open = () => {
            setOpen(root, true);
            setTimeout(() => inputEl.focus(), 0);
            scrollToBottom(messagesEl);
        };
        const close = () => setOpen(root, false);

        if (fab instanceof HTMLButtonElement) {
            fab.addEventListener("click", () => {
                const isOpen = root.classList.contains("chat-open");
                if (isOpen) {
                    close();
                } else {
                    open();
                }
            });
        }

        if (closeBtn instanceof HTMLButtonElement) {
            closeBtn.addEventListener("click", close);
        }

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && root.classList.contains("chat-open")) {
                close();
            }
        });

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            sendChatMessage({ inputEl, sendBtn, messagesEl, history });
        });

        inputEl.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                form.requestSubmit();
            }
        });

        // Auto-grow textarea a bit.
        const autosize = () => {
            inputEl.style.height = "auto";
            inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + "px";
        };
        inputEl.addEventListener("input", autosize);
        autosize();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", buildWidget);
    } else {
        buildWidget();
    }
})();

