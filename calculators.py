from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from config import CAR_INDEX, HOME_CONSTRUCTION_INDEX, HOME_REGION_INDEX, HOME_SECURITY_INDEX, HOME_TYPE_INDEX
from models import HomePremiumInput, PremiumInput


class InsuranceCalculator(ABC):
    @abstractmethod
    def calculate(self, data) -> Dict[str, Any]:
        pass


class PremiumCalculator(InsuranceCalculator):
    BASE_PRICE = 520_000
    PACKAGE_FACTORS: Dict[str, float] = {
        "basic": 1.00,
        "comfort": 1.22,
        "max": 1.48,
    }
    RATING_FACTORS: Dict[str, float] = {
        "experienced": 0.88,
        "standard": 1.00,
        "new": 1.24,
    }
    NO_CLAIM_FACTORS: Dict[int, float] = {
        0: 1.00,
        1: 0.97,
        2: 0.94,
        3: 0.90,
        4: 0.86,
        5: 0.82,
    }
    MODEL_FACTORS: Dict[str, float] = {
        "damas": 0.92,
        "labo": 0.92,
        "cobalt": 1.00,
        "nexia3": 1.00,
        "spark": 0.97,
        "gentra": 1.02,
        "lacetti": 1.04,
        "onix": 1.01,
        "tracker": 1.08,
        "malibu2": 1.12,
        "captiva": 1.15,
        "kia_k5": 1.13,
        "kia_sonet": 1.05,
        "hyundai_elantra": 1.08,
        "hyundai_tucson": 1.11,
        "chery_tiggo7": 1.09,
        "chery_arrizo6": 1.07,
        "haval_jolion": 1.08,
        "byd_song_plus": 1.10,
        "toyota_camry": 1.16,
    }

    def __init__(self, model_factors: Dict[str, float] | None = None) -> None:
        self.model_factors = self.MODEL_FACTORS.copy()
        if model_factors:
            self.model_factors.update(model_factors)

    def calculate(self, data: PremiumInput) -> Dict[str, Any]:
        model_factor = self.model_factors.get(data.model_id, 1.0)
        package_factor = self.PACKAGE_FACTORS[data.package]
        rating_factor = self.RATING_FACTORS[data.rating]
        age_factor = self._vehicle_age_factor(data.year)
        engine_factor = self._engine_factor(data.engine_cc)
        no_claim_factor = self.NO_CLAIM_FACTORS[data.no_claim_years]

        base = float(self.BASE_PRICE)
        after_model = base * model_factor
        after_package = after_model * package_factor
        after_rating = after_package * rating_factor
        after_age = after_rating * age_factor
        before_discount = after_age * engine_factor
        total = before_discount * no_claim_factor

        rounded_total = self._final_total(total)
        monthly = self._round_amount(rounded_total / 12)

        model_name = CAR_INDEX[data.model_id]["name"]["uz"]
        breakdown = [
            {"key": "base", "label": "Asosiy tarif", "value": self._round_amount(base)},
            {"key": "model", "label": "Model koeffitsienti", "value": self._round_amount(after_model - base)},
            {"key": "package", "label": "Paket ta'siri", "value": self._round_amount(after_package - after_model)},
            {"key": "driver", "label": "Haydovchi toifasi", "value": self._round_amount(after_rating - after_package)},
            {"key": "age", "label": "Avtomobil yoshi", "value": self._round_amount(after_age - after_rating)},
            {"key": "engine", "label": "Dvigatel koeffitsienti", "value": self._round_amount(before_discount - after_age)},
            {"key": "discount", "label": "Bonus chegirma", "value": self._round_amount(rounded_total - before_discount)},
        ]

        return {
            "price": rounded_total,
            "monthly": monthly,
            "currency": "UZS",
            "breakdown": breakdown,
            "meta": {
                "vehicle_age": datetime.now().year - data.year,
                "engine_cc": data.engine_cc,
                "package": data.package,
                "rating": data.rating,
                "no_claim_years": data.no_claim_years,
                "model_id": data.model_id,
                "model_name": model_name,
            },
        }

    @staticmethod
    def _vehicle_age_factor(year: int) -> float:
        age = datetime.now().year - year
        if age <= 1:
            return 1.08
        if age <= 5:
            return 1.00
        if age <= 10:
            return 1.12
        return 1.27

    @staticmethod
    def _engine_factor(engine_cc: int) -> float:
        if engine_cc <= 1200:
            return 0.92
        if engine_cc <= 1600:
            return 0.96
        if engine_cc <= 2500:
            return 1.00
        if engine_cc <= 3500:
            return 1.15
        return 1.32

    @staticmethod
    def _round_amount(value: float) -> int:
        return int(round(value, -2))

    @classmethod
    def _final_total(cls, value: float) -> int:
        return cls._round_amount(max(value, 320_000))


class HomePremiumCalculator(InsuranceCalculator):
    BASE_PRICE = 280_000
    PACKAGE_FACTORS: Dict[str, float] = {
        "basic": 1.00,
        "comfort": 1.22,
        "max": 1.48,
    }
    NO_CLAIM_FACTORS: Dict[int, float] = {
        0: 1.00,
        1: 0.98,
        2: 0.95,
        3: 0.92,
        4: 0.88,
        5: 0.84,
    }

    def calculate(self, data: HomePremiumInput) -> Dict[str, Any]:
        type_factor = float(HOME_TYPE_INDEX[data.property_type]["factor"])
        construction_factor = float(HOME_CONSTRUCTION_INDEX[data.construction]["factor"])
        region_factor = float(HOME_REGION_INDEX[data.region]["factor"])
        security_factor = float(HOME_SECURITY_INDEX[data.security]["factor"])
        package_factor = self.PACKAGE_FACTORS[data.package]
        no_claim_factor = self.NO_CLAIM_FACTORS[data.no_claim_years]

        area_factor = self._area_factor(data.area_sqm)
        age_factor = self._home_age_factor(data.build_year)

        base = float(self.BASE_PRICE)
        after_area = base * area_factor
        after_type = after_area * type_factor
        after_construction = after_type * construction_factor
        after_age = after_construction * age_factor
        after_security = after_age * security_factor
        after_package = after_security * package_factor
        before_discount = after_package * region_factor
        total = before_discount * no_claim_factor

        rounded_total = self._final_total(total)
        monthly = self._round_amount(rounded_total / 12)

        breakdown = [
            {"key": "base", "label": "Asosiy tarif", "value": self._round_amount(base)},
            {"key": "area", "label": "Maydon koeffitsienti", "value": self._round_amount(after_area - base)},
            {"key": "home_type", "label": "Uy turi", "value": self._round_amount(after_type - after_area)},
            {"key": "construction", "label": "Qurilish turi", "value": self._round_amount(after_construction - after_type)},
            {"key": "home_age", "label": "Uy yoshi", "value": self._round_amount(after_age - after_construction)},
            {"key": "security", "label": "Xavfsizlik", "value": self._round_amount(after_security - after_age)},
            {"key": "package", "label": "Paket ta'siri", "value": self._round_amount(after_package - after_security)},
            {"key": "region", "label": "Hudud riski", "value": self._round_amount(before_discount - after_package)},
            {"key": "discount", "label": "Bonus chegirma", "value": self._round_amount(rounded_total - before_discount)},
        ]

        region_name = HOME_REGION_INDEX[data.region]["name"]["uz"]
        type_name = HOME_TYPE_INDEX[data.property_type]["name"]["uz"]
        construction_name = HOME_CONSTRUCTION_INDEX[data.construction]["name"]["uz"]
        security_name = HOME_SECURITY_INDEX[data.security]["name"]["uz"]

        return {
            "price": rounded_total,
            "monthly": monthly,
            "currency": "UZS",
            "breakdown": breakdown,
            "meta": {
                "area_sqm": data.area_sqm,
                "build_year": data.build_year,
                "home_age": datetime.now().year - data.build_year,
                "package": data.package,
                "no_claim_years": data.no_claim_years,
                "property_type": data.property_type,
                "property_type_name": type_name,
                "construction": data.construction,
                "construction_name": construction_name,
                "security": data.security,
                "security_name": security_name,
                "region": data.region,
                "region_name": region_name,
            },
        }

    @staticmethod
    def _area_factor(area_sqm: int) -> float:
        if area_sqm <= 40:
            return 0.86
        if area_sqm <= 80:
            return 1.00
        if area_sqm <= 120:
            return 1.12
        if area_sqm <= 200:
            return 1.26
        return 1.42

    @staticmethod
    def _home_age_factor(build_year: int) -> float:
        age = datetime.now().year - build_year
        if age <= 5:
            return 0.96
        if age <= 15:
            return 1.00
        if age <= 30:
            return 1.12
        return 1.26

    @staticmethod
    def _round_amount(value: float) -> int:
        return int(round(value, -2))

    @classmethod
    def _final_total(cls, value: float) -> int:
        return cls._round_amount(max(value, 250_000))
