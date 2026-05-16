import re
from datetime import datetime
from pathlib import Path
from typing import Any, List
from uuid import uuid4

from werkzeug.utils import secure_filename

from config import ALLOWED_IMAGE_EXTENSIONS, CAR_INDEX
from models import PremiumInput, ValidationError, HomePremiumInput
from calculators import PremiumCalculator
from database import get_model_factors, get_db_connection


def validate_email(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value))


def round_amount(value: float) -> int:
    return int(round(value, -2))


def normalize_car_photo_path(value: Any, app_root_path: str) -> str | None:
    photo_path = str(value or "").strip()
    if not photo_path:
        return None
    if not photo_path.startswith("/static/uploads/cars/"):
        raise ValidationError("Rasm manzili noto'g'ri.")
    disk_path = Path(app_root_path).joinpath(*photo_path.lstrip("/").split("/"))
    if not disk_path.exists():
        raise ValidationError("Yuklangan rasm topilmadi.")
    return photo_path


def save_uploaded_car_photo(file_storage: Any, car_upload_dir: Path) -> str:
    filename = secure_filename(str(getattr(file_storage, "filename", "") or ""))
    if not filename:
        raise ValidationError("Rasm faylini tanlang.")

    suffix = Path(filename).suffix.lower()
    content_type = str(getattr(file_storage, "mimetype", "") or "").lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS or not content_type.startswith("image/"):
        raise ValidationError("Faqat JPG, PNG yoki WEBP rasm yuklang.")

    car_upload_dir.mkdir(parents=True, exist_ok=True)
    saved_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{suffix}"
    target = car_upload_dir / saved_name
    file_storage.save(target)
    return f"/static/uploads/cars/{saved_name}"


def calculate_quote(payload: Any, db_path: Path) -> tuple[PremiumInput, dict[str, Any]]:
    premium_input = PremiumInput.from_payload(payload)
    calculator = PremiumCalculator(model_factors=get_model_factors(db_path))
    quote = calculator.calculate(premium_input)
    return premium_input, quote


def format_order_status_uz(status: str) -> str:
    return {
        "submitted": "Qabul qilingan",
        "paid": "To'langan",
        "cancelled": "Bekor qilingan",
    }.get(str(status).strip().lower(), status)


def format_package_uz(package: str) -> str:
    return {
        "basic": "Asosiy",
        "comfort": "Qulay",
        "max": "Maksimal",
    }.get(str(package).strip().lower(), package)


def format_driver_rating_uz(rating: str) -> str:
    return {
        "experienced": "Tajribali haydovchi",
        "standard": "Oddiy haydovchi",
        "new": "Yangi haydovchi",
    }.get(str(rating).strip().lower(), rating)


def escape_pdf(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_simple_pdf(lines: list[str]) -> bytes:
    ops = ["BT", "/F1 12 Tf", "50 790 Td"]
    for idx, line in enumerate(lines):
        if idx > 0:
            ops.append("0 -18 Td")
        ops.append(f"({escape_pdf(line)}) Tj")
    ops.append("ET")
    stream = "\n".join(ops).encode("latin-1", "replace")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(offsets)} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_start}\n"
            "%%EOF"
        ).encode()
    )
    return bytes(pdf)


class FormCommunicator:
    def __init__(self):
        self.shared_data: dict[str, Any] = {}

    def set_data(self, key: str, value: Any) -> None:
        self.shared_data[key] = value

    def get_data(self, key: str) -> Any:
        return self.shared_data.get(key)
