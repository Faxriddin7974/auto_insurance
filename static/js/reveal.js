(() => {
    const prefersReducedMotion =
        typeof window !== "undefined" &&
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function setVisible(element) {
        element.classList.add("reveal");
        element.classList.add("is-visible");
        element.classList.remove("will-reveal");
    }

    function isElementNode(node) {
        return node && node.nodeType === 1;
    }

    function shouldSkip(element) {
        if (!(element instanceof HTMLElement)) {
            return true;
        }
        if (element.closest(".auth-modal")) {
            return true;
        }
        if (element.classList.contains("hidden")) {
            return true;
        }
        const tag = element.tagName;
        if (tag === "SCRIPT" || tag === "STYLE" || tag === "LINK" || tag === "META" || tag === "NOSCRIPT") {
            return true;
        }
        return false;
    }

    function markReveal(element, options = {}) {
        if (shouldSkip(element)) {
            return;
        }

        element.classList.add("reveal");
        element.classList.add("will-reveal");

        if (
            element.classList.contains("card") ||
            element.classList.contains("summary-item") ||
            element.classList.contains("cabinet-box") ||
            element.classList.contains("faq-item") ||
            element.classList.contains("review-card") ||
            element.classList.contains("admin-form") ||
            element.classList.contains("action-btn") ||
            element.closest(".hero-metrics") ||
            element.closest(".partner-grid")
        ) {
            element.classList.add("reveal-line");
        }

        if (options.variant) {
            element.dataset.reveal = options.variant;
        }
        if (typeof options.delay === "number") {
            element.style.setProperty("--reveal-delay", `${options.delay}ms`);
        }
        if (typeof options.duration === "number") {
            element.style.setProperty("--reveal-duration", `${options.duration}ms`);
        }
    }

    function collectRevealTargets() {
        const root = document.querySelector(".page-shell");
        if (!root) {
            return [];
        }

        const targets = [];
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, {
            acceptNode(node) {
                if (!isElementNode(node)) {
                    return NodeFilter.FILTER_REJECT;
                }
                const element = /** @type {HTMLElement} */ (node);
                if (shouldSkip(element)) {
                    return NodeFilter.FILTER_REJECT;
                }
                // Skip structural wrappers that would animate huge chunks awkwardly.
                if (element.classList.contains("page-shell")) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            },
        });

        let current = walker.nextNode();
        while (current) {
            const element = /** @type {HTMLElement} */ (current);
            targets.push(element);
            current = walker.nextNode();
        }
        return targets;
    }

    function setupVariants() {
        const heroTitle = document.querySelector(".hero h1");
        if (heroTitle instanceof HTMLElement) {
            markReveal(heroTitle, { variant: "up", delay: 80, duration: 720 });
        }

        const heroImage = document.querySelector(".hero-visual img");
        if (heroImage instanceof HTMLElement) {
            markReveal(heroImage, { variant: "right", delay: 140, duration: 920 });
        }

        const metrics = Array.from(document.querySelectorAll(".hero-metrics > *"));
        metrics.forEach((element, index) => {
            if (!(element instanceof HTMLElement)) {
                return;
            }
            markReveal(element, { variant: "up", delay: 220 + index * 100, duration: 520 });
        });
    }

    function init() {
        setupVariants();

        const targets = collectRevealTargets();
        if (targets.length === 0) {
            return;
        }

        // Mark any other visible elements with default reveal settings.
        targets.forEach((element) => {
            if (!element.classList.contains("reveal")) {
                markReveal(element, { variant: "up" });
            }
        });

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            targets.forEach((element) => setVisible(element));
            return;
        }

        const viewportHeight = window.innerHeight || 0;
        const inInitialView = (element) => {
            const rect = element.getBoundingClientRect();
            return rect.bottom > 0 && rect.top < viewportHeight * 0.92;
        };

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    const element = entry.target;
                    if (!(element instanceof HTMLElement)) {
                        return;
                    }
                    if (!entry.isIntersecting) {
                        return;
                    }
                    setVisible(element);
                    observer.unobserve(element);
                });
            },
            { root: null, rootMargin: "0px 0px -10% 0px", threshold: 0.12 }
        );

        const initialTargets = [];
        targets.forEach((element) => {
            if (inInitialView(element)) {
                initialTargets.push(element);
                return;
            }
            observer.observe(element);
        });

        if (initialTargets.length > 0) {
            requestAnimationFrame(() => {
                initialTargets.forEach((element) => setVisible(element));
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
