let premiumChart = null;
let currentLanguage = "uz";
let carData = [];
let homeCatalog = null;
let yearRange = { min: 1980, max: new Date().getFullYear() + 1 };
let lastBreakdown = [];
let lastQuotePayload = null;
let lastQuoteResult = null;
let lastOrderId = null;
let currentUser = null;
let lastCarPhoto = null;
let googleIdentityInitialized = false;

try {
    const savedLanguage = window.localStorage ? window.localStorage.getItem("app_lang") : null;
    if (savedLanguage) {
        currentLanguage = savedLanguage;
    }
} catch (error) {
    currentLanguage = "uz";
}

