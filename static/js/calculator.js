function populateYearSelect() {
    const select = document.getElementById("year_select");
    if (!select) {
        return;
    }
    const selected = Number(select.value) || yearRange.max;
    select.innerHTML = "";

    for (let year = yearRange.max; year >= yearRange.min; year -= 1) {
        const option = document.createElement("option");
        option.value = String(year);
        option.textContent = String(year);
        if (year === selected) {
            option.selected = true;
        }
        select.appendChild(option);
    }
}

function populateCarModels() {
    const modelSelect = document.getElementById("car_model");
    if (!modelSelect) {
        return;
    }
    const previous = modelSelect.value;
    modelSelect.innerHTML = "";

    carData.forEach((car) => {
        const option = document.createElement("option");
        option.value = car.id;
        option.textContent = car.name[currentLanguage] || car.name.uz;
        if (car.id === previous) {
            option.selected = true;
        }
        modelSelect.appendChild(option);
    });

    if (!modelSelect.value && carData.length > 0) {
        modelSelect.value = carData[0].id;
    }

    populateEngines(modelSelect.value);
}

function populateEngines(modelId) {
    const engineSelect = document.getElementById("engine_select");
    if (!engineSelect) {
        return;
    }
    engineSelect.innerHTML = "";

    const model = carData.find((item) => item.id === modelId);
    const engines = model && Array.isArray(model.engines) ? model.engines : [];

    engines.forEach((engineValue) => {
        const option = document.createElement("option");
        option.value = String(engineValue);
        option.textContent = `${engineValue} sm3`;
        engineSelect.appendChild(option);
    });
}

function fillSelectOptions(select, items) {
    if (!select) {
        return;
    }
    const previous = select.value;
    select.innerHTML = "";

    (items || []).forEach((item) => {
        const option = document.createElement("option");
        option.value = String(item.id);
        if (item && item.name) {
            option.textContent = item.name[currentLanguage] || item.name.uz || String(item.id);
        } else {
            option.textContent = String(item.id);
        }
        select.appendChild(option);
    });

    if (previous) {
        select.value = previous;
    }
    if (!select.value && items && items.length > 0) {
        select.value = String(items[0].id);
    }
}

function populateHomeSelects() {
    if (!homeCatalog) {
        return;
    }
    fillSelectOptions(document.getElementById("home_type"), homeCatalog.property_types);
    fillSelectOptions(document.getElementById("home_construction"), homeCatalog.construction_types);
    fillSelectOptions(document.getElementById("home_region"), homeCatalog.regions);
    fillSelectOptions(document.getElementById("home_security"), homeCatalog.security_levels);
}

function updateYearModeUI() {
    const yearModeInput = document.getElementById("year_mode");
    const manualWrap = document.getElementById("yearManualWrap");
    const selectWrap = document.getElementById("yearSelectWrap");
    if (!yearModeInput || !manualWrap || !selectWrap) {
        return;
    }
    const yearMode = yearModeInput.value;

    if (yearMode === "manual") {
        manualWrap.classList.remove("hidden");
        selectWrap.classList.add("hidden");
    } else {
        manualWrap.classList.add("hidden");
        selectWrap.classList.remove("hidden");
    }
}

function getYearValue() {
    const yearModeInput = document.getElementById("year_mode");
    if (!yearModeInput) {
        return NaN;
    }
    const yearMode = yearModeInput.value;
    if (yearMode === "manual") {
        return Number(document.getElementById("year_manual").value);
    }
    return Number(document.getElementById("year_select").value);
}

function renderBreakdown(items) {
    const list = document.getElementById("breakdownList");
    if (!list) {
        return;
    }
    list.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = `<li class='placeholder'>${t("placeholder.details")}</li>`;
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        if (Number(item.value) < 0) {
            li.classList.add("negative");
        }

        const label = document.createElement("span");
        const langPack = TRANSLATIONS[currentLanguage] || {};
        const translatedLabel = langPack[`breakdown.${item.key}`];
        label.textContent = translatedLabel || item.label;

        const value = document.createElement("strong");
        const sign = Number(item.value) > 0 ? "+" : "";
        value.textContent = `${sign}${formatCurrency(item.value)}`;

        li.appendChild(label);
        li.appendChild(value);
        list.appendChild(li);
    });
}

function renderChart(items) {
    const canvas = document.getElementById("myChart");
    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const ctx = canvas.getContext("2d");
    const isSmallScreen = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(max-width: 520px)").matches;
    const labels = items.map((item) => {
        const langPack = TRANSLATIONS[currentLanguage] || {};
        const translatedLabel = langPack[`breakdown.${item.key}`];
        return translatedLabel || item.label;
    });
    const values = items.map((item) => Math.abs(Number(item.value) || 0));
    const colors = items.map((item) =>
        Number(item.value) < 0 ? "rgba(45, 212, 191, 0.85)" : "rgba(245, 158, 11, 0.85)"
    );

    if (premiumChart) {
        premiumChart.destroy();
    }

    premiumChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: isSmallScreen ? 26 : 34,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label(context) {
                            return formatCurrency(context.parsed.y);
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: "rgba(213, 228, 239, 0.75)",
                        autoSkip: isSmallScreen,
                        maxRotation: isSmallScreen ? 45 : 0,
                        minRotation: isSmallScreen ? 45 : 0,
                        font: { size: isSmallScreen ? 10 : 11 },
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: "rgba(255, 255, 255, 0.08)" },
                    ticks: {
                        color: "rgba(213, 228, 239, 0.75)",
                        callback(value) {
                            return Number(value).toLocaleString(localeByLang[currentLanguage]);
                        },
                    },
                },
            },
        },
    });
}

async function loadCars() {
    setMessage("msg.loadingCars", "", true);
    const data = await requestJSON("/car-data");
    carData = Array.isArray(data.cars) ? data.cars : [];
    yearRange = {
        min: Number(data.year_min) || 1980,
        max: Number(data.year_max) || new Date().getFullYear() + 1,
    };
    populateYearSelect();
    populateCarModels();
    if (currentUser && currentUser.is_admin) {
        loadAdminData();
    }
    setMessage("");
}

async function loadHomeData() {
    setMessage("home.msg.loading", "", true);
    const data = await requestJSON("/home-data");
    homeCatalog = {
        property_types: Array.isArray(data.property_types) ? data.property_types : [],
        construction_types: Array.isArray(data.construction_types) ? data.construction_types : [],
        regions: Array.isArray(data.regions) ? data.regions : [],
        security_levels: Array.isArray(data.security_levels) ? data.security_levels : [],
    };
    yearRange = {
        min: Number(data.year_min) || 1950,
        max: Number(data.year_max) || new Date().getFullYear(),
    };
    populateYearSelect();
    populateHomeSelects();
    setMessage("");
}

function validateInputs(payload) {
    if (!payload.model_id) {
        return t("msg.selectModel");
    }

    if (!Number.isInteger(payload.year)) {
        return t("msg.yearRequired");
    }

    if (payload.year < yearRange.min || payload.year > yearRange.max) {
        return `${t("msg.yearRange")} (${yearRange.min}-${yearRange.max})`;
    }

    return "";
}

function validateHomeInputs(payload) {
    if (!payload.property_type) {
        return t("home.msg.typeRequired");
    }

    if (!Number.isFinite(payload.area_sqm) || payload.area_sqm <= 0) {
        return t("home.msg.areaRequired");
    }

    if (payload.area_sqm < 15 || payload.area_sqm > 1500) {
        return `${t("home.msg.areaRange")} (15-1500)`;
    }

    if (!Number.isInteger(payload.build_year)) {
        return t("home.msg.yearRequired");
    }

    if (payload.build_year < yearRange.min || payload.build_year > yearRange.max) {
        return `${t("home.msg.yearRange")} (${yearRange.min}-${yearRange.max})`;
    }

    return "";
}

async function handleCalculation(event) {
    event.preventDefault();

    const button = document.getElementById("calculateBtn");
    const payload = {
        model_id: document.getElementById("car_model").value,
        engine: Number(document.getElementById("engine_select").value),
        year: getYearValue(),
        package: document.getElementById("package").value,
        rating: document.getElementById("rating").value,
        no_claim_years: Number(document.getElementById("no_claim_years").value),
        car_photo_path: lastCarPhoto ? lastCarPhoto.path : "",
    };

    const validationError = validateInputs(payload);
    if (validationError) {
        setMessage(validationError, "error");
        return;
    }

    button.disabled = true;
    button.textContent = `${t("calc.submit")}...`;
    setMessage("msg.calculating", "", true);

    try {
        const data = await requestJSON("/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        lastQuotePayload = payload;
        lastQuoteResult = data;
        lastOrderId = null;
        document.getElementById("pdfBtn").disabled = true;
        document.getElementById("telegramBtn").disabled = true;
        const paymentLink = document.getElementById("paymentLink");
        if (paymentLink) {
            paymentLink.classList.add("hidden");
            paymentLink.setAttribute("href", "#");
        }
        lastBreakdown = data.breakdown || [];
        document.getElementById("result").textContent = formatCurrency(data.price);
        document.getElementById("monthlyResult").textContent = formatCurrency(data.monthly);
        document.getElementById("updatedAt").textContent = new Date().toLocaleTimeString(localeByLang[currentLanguage], {
            hour: "2-digit",
            minute: "2-digit",
        });

        renderBreakdown(lastBreakdown);
        renderChart(lastBreakdown);
        setMessage("msg.done", "success", true);
    } catch (error) {
        setMessage(error.message, "error");
    } finally {
        button.disabled = false;
        button.textContent = t("calc.submit");
    }
}

async function handleHomeCalculation(event) {
    event.preventDefault();

    const button = document.getElementById("homeCalculateBtn");
    const payload = {
        property_type: document.getElementById("home_type").value,
        area_sqm: Number(document.getElementById("home_area").value),
        construction: document.getElementById("home_construction").value,
        region: document.getElementById("home_region").value,
        security: document.getElementById("home_security").value,
        build_year: getYearValue(),
        package: document.getElementById("home_package").value,
        no_claim_years: Number(document.getElementById("home_no_claim_years").value),
    };

    const validationError = validateHomeInputs(payload);
    if (validationError) {
        setMessage(validationError, "error");
        return;
    }

    if (button) {
        button.disabled = true;
        button.textContent = `${t("home.calc.submit")}...`;
    }
    setMessage("msg.calculating", "", true);

    try {
        const data = await requestJSON("/calculate-home", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        lastQuotePayload = payload;
        lastQuoteResult = data;
        lastOrderId = null;
        lastBreakdown = data.breakdown || [];

        document.getElementById("result").textContent = formatCurrency(data.price);
        document.getElementById("monthlyResult").textContent = formatCurrency(data.monthly);
        document.getElementById("updatedAt").textContent = new Date().toLocaleTimeString(localeByLang[currentLanguage], {
            hour: "2-digit",
            minute: "2-digit",
        });

        renderBreakdown(lastBreakdown);
        renderChart(lastBreakdown);
        setMessage("msg.done", "success", true);
    } catch (error) {
        setMessage(error.message, "error");
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = t("home.calc.submit");
        }
    }
}

