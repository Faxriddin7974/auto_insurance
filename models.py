from dataclasses import dataclass
from datetime import datetime
from typing import Any

from config import (
    CAR_INDEX,
    HOME_CONSTRUCTION_INDEX,
    HOME_REGION_INDEX,
    HOME_SECURITY_INDEX,
    HOME_TYPE_INDEX,
    HOME_YEAR_MIN,
)


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class PremiumInput:
    year: int
    engine_cc: int
    package: str
    rating: str
    no_claim_years: int
    model_id: str

    @classmethod
    def from_payload(cls, payload: Any) -> "PremiumInput":
        if not isinstance(payload, dict):
            raise ValidationError("Noto'g'ri so'rov formati.")

        model_id = str(payload.get("model_id", "")).strip().lower()
        year = cls._as_int(payload.get("year"), "Mashina yili raqam bo'lishi kerak.")
        engine_cc = cls._as_int(payload.get("engine"), "Dvigatel hajmi raqam bo'lishi kerak.")
        no_claim_years = cls._as_int(payload.get("no_claim_years", 0), "Avariya qilmagan yillar qiymati noto'g'ri.")

        package = str(payload.get("package", "")).strip().lower()
        rating = str(payload.get("rating", "")).strip().lower()

        validate_vehicle_selection(model_id=model_id, engine_cc=engine_cc, year=year)

        if package not in {"basic", "comfort", "max"}:
            raise ValidationError("Sug'urta paketi noto'g'ri tanlangan.")
        if rating not in {"experienced", "standard", "new"}:
            raise ValidationError("Haydovchi toifasi noto'g'ri tanlangan.")
        if no_claim_years < 0 or no_claim_years > 5:
            raise ValidationError("Avariya qilmagan yillar 0 dan 5 gacha bo'lishi kerak.")

        return cls(
            year=year,
            engine_cc=engine_cc,
            package=package,
            rating=rating,
            no_claim_years=no_claim_years,
            model_id=model_id,
        )

    @staticmethod
    def _as_int(value: Any, message: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(message) from exc


@dataclass(frozen=True)
class HomePremiumInput:
    build_year: int
    area_sqm: int
    package: str
    no_claim_years: int
    property_type: str
    construction: str
    region: str
    security: str

    @classmethod
    def from_payload(cls, payload: Any) -> "HomePremiumInput":
        if not isinstance(payload, dict):
            raise ValidationError("Noto'g'ri so'rov formati.")

        property_type = str(payload.get("property_type", "")).strip().lower()
        construction = str(payload.get("construction", "")).strip().lower()
        region = str(payload.get("region", "")).strip().lower()
        security = str(payload.get("security", "")).strip().lower()

        build_year = cls._as_int(payload.get("build_year"), "Qurilgan yil raqam bo'lishi kerak.")
        area_sqm = cls._as_int(payload.get("area_sqm"), "Maydon raqam bo'lishi kerak.")
        no_claim_years = cls._as_int(payload.get("no_claim_years", 0), "Zarar bo'lmagan yillar qiymati noto'g'ri.")

        package = str(payload.get("package", "")).strip().lower()

        validate_home_selection(
            property_type=property_type,
            construction=construction,
            region=region,
            security=security,
            build_year=build_year,
            area_sqm=area_sqm,
        )

        if package not in {"basic", "comfort", "max"}:
            raise ValidationError("Sug'urta paketi noto'g'ri tanlangan.")
        if no_claim_years < 0 or no_claim_years > 5:
            raise ValidationError("Zarar bo'lmagan yillar 0 dan 5 gacha bo'lishi kerak.")

        return cls(
            build_year=build_year,
            area_sqm=area_sqm,
            package=package,
            no_claim_years=no_claim_years,
            property_type=property_type,
            construction=construction,
            region=region,
            security=security,
        )

    @staticmethod
    def _as_int(value: Any, message: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(message) from exc


def validate_vehicle_selection(*, model_id: str, engine_cc: int, year: int) -> None:
    current_year = datetime.now().year
    if model_id not in CAR_INDEX:
        raise ValidationError("Avtomobil modeli noto'g'ri tanlangan.")
    if year < 1980 or year > current_year + 1:
        raise ValidationError(f"Mashina yili 1980 va {current_year + 1} oralig'ida bo'lishi kerak.")
    if engine_cc < 800 or engine_cc > 7000:
        raise ValidationError("Dvigatel hajmi 800 va 7000 sm3 oralig'ida bo'lishi kerak.")
    if engine_cc not in CAR_INDEX[model_id]["engines"]:
        raise ValidationError("Tanlangan model uchun dvigatel hajmi mos emas.")


def validate_home_selection(
    *,
    property_type: str,
    construction: str,
    region: str,
    security: str,
    build_year: int,
    area_sqm: int,
) -> None:
    current_year = datetime.now().year
    if property_type not in HOME_TYPE_INDEX:
        raise ValidationError("Uy turi noto'g'ri tanlangan.")
    if construction not in HOME_CONSTRUCTION_INDEX:
        raise ValidationError("Qurilish turi noto'g'ri tanlangan.")
    if region not in HOME_REGION_INDEX:
        raise ValidationError("Hudud noto'g'ri tanlangan.")
    if security not in HOME_SECURITY_INDEX:
        raise ValidationError("Xavfsizlik parametri noto'g'ri tanlangan.")
    if build_year < HOME_YEAR_MIN or build_year > current_year:
        raise ValidationError(f"Qurilgan yil {HOME_YEAR_MIN} va {current_year} oralig'ida bo'lishi kerak.")
    if area_sqm < 15 or area_sqm > 1500:
        raise ValidationError("Maydon 15 va 1500 m2 oralig'ida bo'lishi kerak.")
