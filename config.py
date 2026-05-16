import os
from pathlib import Path
from typing import Any, Dict, List

FLASK_SECRET_KEY = "dev-secret-key-change-me"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()

ORDER_STATUSES: set[str] = {"submitted", "paid", "cancelled"}
REVIEW_STATUSES: set[str] = {"pending", "approved", "rejected"}

HOME_YEAR_MIN = 1950

TOP_CARS: List[Dict[str, Any]] = [
    {"id": "cobalt", "name": {"uz": "Chevrolet Cobalt", "en": "Chevrolet Cobalt", "ru": "Chevrolet Cobalt"}, "engines": [1500]},
    {"id": "nexia3", "name": {"uz": "Chevrolet Nexia 3", "en": "Chevrolet Nexia 3", "ru": "Chevrolet Nexia 3"}, "engines": [1500]},
    {"id": "damas", "name": {"uz": "Chevrolet Damas", "en": "Chevrolet Damas", "ru": "Chevrolet Damas"}, "engines": [800]},
    {"id": "labo", "name": {"uz": "Chevrolet Labo", "en": "Chevrolet Labo", "ru": "Chevrolet Labo"}, "engines": [800]},
    {"id": "spark", "name": {"uz": "Chevrolet Spark", "en": "Chevrolet Spark", "ru": "Chevrolet Spark"}, "engines": [1250]},
    {"id": "lacetti", "name": {"uz": "Chevrolet Lacetti", "en": "Chevrolet Lacetti", "ru": "Chevrolet Lacetti"}, "engines": [1600, 1800]},
    {"id": "gentra", "name": {"uz": "Chevrolet Gentra", "en": "Chevrolet Gentra", "ru": "Chevrolet Gentra"}, "engines": [1500]},
    {"id": "tracker", "name": {"uz": "Chevrolet Tracker", "en": "Chevrolet Tracker", "ru": "Chevrolet Tracker"}, "engines": [1200, 2000]},
    {"id": "onix", "name": {"uz": "Chevrolet Onix", "en": "Chevrolet Onix", "ru": "Chevrolet Onix"}, "engines": [1200]},
    {"id": "malibu2", "name": {"uz": "Chevrolet Malibu 2", "en": "Chevrolet Malibu 2", "ru": "Chevrolet Malibu 2"}, "engines": [1500, 2000]},
    {"id": "captiva", "name": {"uz": "Chevrolet Captiva", "en": "Chevrolet Captiva", "ru": "Chevrolet Captiva"}, "engines": [2400, 3000]},
    {"id": "kia_k5", "name": {"uz": "Kia K5", "en": "Kia K5", "ru": "Kia K5"}, "engines": [2000, 2500]},
    {"id": "kia_sonet", "name": {"uz": "Kia Sonet", "en": "Kia Sonet", "ru": "Kia Sonet"}, "engines": [1500]},
    {"id": "hyundai_elantra", "name": {"uz": "Hyundai Elantra", "en": "Hyundai Elantra", "ru": "Hyundai Elantra"}, "engines": [1600, 2000]},
    {"id": "hyundai_tucson", "name": {"uz": "Hyundai Tucson", "en": "Hyundai Tucson", "ru": "Hyundai Tucson"}, "engines": [2000, 2500]},
    {"id": "chery_tiggo7", "name": {"uz": "Chery Tiggo 7 Pro", "en": "Chery Tiggo 7 Pro", "ru": "Chery Tiggo 7 Pro"}, "engines": [1500, 1600]},
    {"id": "chery_arrizo6", "name": {"uz": "Chery Arrizo 6 Pro", "en": "Chery Arrizo 6 Pro", "ru": "Chery Arrizo 6 Pro"}, "engines": [1500]},
    {"id": "haval_jolion", "name": {"uz": "Haval Jolion", "en": "Haval Jolion", "ru": "Haval Jolion"}, "engines": [1500]},
    {"id": "byd_song_plus", "name": {"uz": "BYD Song Plus", "en": "BYD Song Plus", "ru": "BYD Song Plus"}, "engines": [1500]},
    {"id": "toyota_camry", "name": {"uz": "Toyota Camry", "en": "Toyota Camry", "ru": "Toyota Camry"}, "engines": [2000, 2500, 3500]},
]

CAR_INDEX: Dict[str, Dict[str, Any]] = {car["id"]: car for car in TOP_CARS}

HOME_PROPERTY_TYPES: List[Dict[str, Any]] = [
    {"id": "apartment", "name": {"uz": "Kvartira", "en": "Apartment", "ru": "Квартира"}, "factor": 1.00},
    {"id": "house", "name": {"uz": "Xususiy uy", "en": "House", "ru": "Частный дом"}, "factor": 1.08},
    {"id": "cottage", "name": {"uz": "Kottej", "en": "Cottage", "ru": "Коттедж"}, "factor": 1.15},
]

HOME_CONSTRUCTION_TYPES: List[Dict[str, Any]] = [
    {"id": "brick", "name": {"uz": "G'isht", "en": "Brick", "ru": "Кирпич"}, "factor": 1.00},
    {"id": "panel", "name": {"uz": "Panel", "en": "Panel", "ru": "Панель"}, "factor": 1.05},
    {"id": "monolith", "name": {"uz": "Monolit", "en": "Monolith", "ru": "Монолит"}, "factor": 0.97},
]

HOME_SECURITY_LEVELS: List[Dict[str, Any]] = [
    {"id": "none", "name": {"uz": "Yo'q", "en": "None", "ru": "Нет"}, "factor": 1.00},
    {"id": "alarm", "name": {"uz": "Signalizatsiya", "en": "Alarm", "ru": "Сигнализация"}, "factor": 0.95},
    {"id": "guard", "name": {"uz": "Qo'riqlash", "en": "Guarded", "ru": "Охрана"}, "factor": 0.90},
]

HOME_REGIONS: List[Dict[str, Any]] = [
    {"id": "tashkent_city", "name": {"uz": "Toshkent sh.", "en": "Tashkent city", "ru": "г. Ташкент"}, "factor": 1.12},
    {"id": "tashkent", "name": {"uz": "Toshkent vil.", "en": "Tashkent region", "ru": "Ташкентская обл."}, "factor": 1.06},
    {"id": "andijan", "name": {"uz": "Andijon", "en": "Andijan", "ru": "Андижан"}, "factor": 1.03},
    {"id": "bukhara", "name": {"uz": "Buxoro", "en": "Bukhara", "ru": "Бухара"}, "factor": 1.01},
    {"id": "fergana", "name": {"uz": "Farg'ona", "en": "Fergana", "ru": "Фергана"}, "factor": 1.03},
    {"id": "jizzakh", "name": {"uz": "Jizzax", "en": "Jizzakh", "ru": "Джизак"}, "factor": 1.00},
    {"id": "kashkadarya", "name": {"uz": "Qashqadaryo", "en": "Kashkadarya", "ru": "Кашкадарья"}, "factor": 1.00},
    {"id": "khorezm", "name": {"uz": "Xorazm", "en": "Khorezm", "ru": "Хорезм"}, "factor": 1.00},
    {"id": "namangan", "name": {"uz": "Namangan", "en": "Namangan", "ru": "Наманган"}, "factor": 1.02},
    {"id": "navoi", "name": {"uz": "Navoiy", "en": "Navoi", "ru": "Навои"}, "factor": 1.00},
    {"id": "samarkand", "name": {"uz": "Samarqand", "en": "Samarkand", "ru": "Самарканд"}, "factor": 1.02},
    {"id": "surkhandarya", "name": {"uz": "Surxondaryo", "en": "Surkhandarya", "ru": "Сурхандарья"}, "factor": 1.00},
    {"id": "syrdarya", "name": {"uz": "Sirdaryo", "en": "Syrdarya", "ru": "Сырдарья"}, "factor": 1.00},
    {"id": "karakalpakstan", "name": {"uz": "Qoraqalpog'iston", "en": "Karakalpakstan", "ru": "Каракалпакстан"}, "factor": 1.00},
]

HOME_TYPE_INDEX: Dict[str, Dict[str, Any]] = {item["id"]: item for item in HOME_PROPERTY_TYPES}
HOME_CONSTRUCTION_INDEX: Dict[str, Dict[str, Any]] = {item["id"]: item for item in HOME_CONSTRUCTION_TYPES}
HOME_SECURITY_INDEX: Dict[str, Dict[str, Any]] = {item["id"]: item for item in HOME_SECURITY_LEVELS}
HOME_REGION_INDEX: Dict[str, Dict[str, Any]] = {item["id"]: item for item in HOME_REGIONS}
