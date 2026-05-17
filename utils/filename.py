"""리포트 파일명 빌드 + 존재 확인 유틸.

파일명 형식: {타입}_{연령}_{월}_{주차}.jpg
예: 스팀월활동_01세_05월_03주.jpg
"""
from pathlib import Path
from utils.mapping import TYPE_STEAM, TYPE_ART


REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def build_filename(type_code: str, age_code: str, month_code: str, week_code: str) -> str:
    """type_code는 TYPE_STEAM 또는 TYPE_ART."""
    return f"{type_code}_{age_code}_{month_code}_{week_code}.jpg"


def build_path(type_code: str, age_code: str, month_code: str, week_code: str) -> Path:
    return REPORTS_DIR / build_filename(type_code, age_code, month_code, week_code)


def report_exists(type_code: str, age_code: str, month_code: str, week_code: str) -> bool:
    return build_path(type_code, age_code, month_code, week_code).exists()


def steam_path(age_code: str, month_code: str, week_code: str) -> Path:
    return build_path(TYPE_STEAM, age_code, month_code, week_code)


def art_path(age_code: str, month_code: str, week_code: str) -> Path:
    return build_path(TYPE_ART, age_code, month_code, week_code)
