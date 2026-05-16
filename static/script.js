(() => {
    const scriptParts = [
        "/static/js/state.js",
        "/static/js/translations.js",
        "/static/js/core.js",
        "/static/js/chat-widget.js",
        "/static/js/reveal.js",
        "/static/js/reviews.js",
        "/static/js/auth.js",
        "/static/js/admin.js",
        "/static/js/calculator.js",
        "/static/js/app-init.js",
    ];

    function loadPart(index) {
        if (index >= scriptParts.length) {
            return;
        }

        const script = document.createElement("script");
        script.src = scriptParts[index];
        script.async = false;
        script.onload = () => loadPart(index + 1);
        script.onerror = () => {
            console.error(`Failed to load script part: ${scriptParts[index]}`);
        };
        document.head.appendChild(script);
    }

    loadPart(0);
})();

