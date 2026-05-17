"""결과 페이지의 lookup 로직 캡슐화.

query_params 파싱 → 검증 → ReportContext 또는 QueryError 반환.
Streamlit에 의존하지 않는 순수 로직 (테스트 용이성).
"""
from dataclasses import dataclass
from pathlib import Path

from utils.mapping import (
    is_valid_age_code, is_valid_month_code, is_valid_week_code,
    age_code_to_label, month_code_to_label, week_code_to_label,
    TYPE_STEAM, TYPE_ART,
)
from utils.filename import steam_path, art_path


# 사용자 표시용 타입 라벨
TYPE_LABEL_STEAM = "STEAM WALL 활동"
TYPE_LABEL_ART = "아트 활동"


@dataclass
class ReportItem:
    """단일 리포트 항목 (스팀월 또는 아트)."""
    type_code: str          # "스팀월활동" 또는 "아트활동"
    type_label: str         # "STEAM WALL 활동" 또는 "아트 활동"
    path: Path              # /reports/스팀월활동_01세_05월_03주.jpg
    exists: bool            # 파일 존재 여부


@dataclass
class ReportContext:
    """결과 페이지 렌더링에 필요한 전체 정보."""
    age_code: str
    month_code: str
    week_code: str
    age_label: str
    month_label: str
    week_label: str
    items: list[ReportItem]

    @property
    def has_any_existing(self) -> bool:
        return any(item.exists for item in self.items)


@dataclass
class QueryError:
    """잘못된 쿼리 파라미터로 인한 오류."""
    message: str


def load_from_query_params(qp) -> "ReportContext | QueryError":
    """st.query_params(dict-like)을 받아 ReportContext 또는 QueryError 반환.

    qp는 dict-like (`.get(key, default)` 지원) 객체.
    """
    age = qp.get("age", "")
    month = qp.get("month", "")
    week = qp.get("week", "")
    has_steam = qp.get("steam", "") == "1"
    has_art = qp.get("art", "") == "1"

    # 검증
    errors = []
    if not is_valid_age_code(age):
        errors.append(f"연령 코드 오류: {age!r}")
    if not is_valid_month_code(month):
        errors.append(f"월 코드 오류: {month!r}")
    if not is_valid_week_code(week):
        errors.append(f"주차 코드 오류: {week!r}")
    if not (has_steam or has_art):
        errors.append("STEAM WALL 또는 Art 카테고리 플래그(steam/art)가 없습니다")

    if errors:
        return QueryError(message=" / ".join(errors))

    # ReportItem 빌드 — STEAM이 먼저 (Sprint 2 인수 조건)
    items: list[ReportItem] = []
    if has_steam:
        p = steam_path(age, month, week)
        items.append(ReportItem(
            type_code=TYPE_STEAM,
            type_label=TYPE_LABEL_STEAM,
            path=p,
            exists=p.exists(),
        ))
    if has_art:
        p = art_path(age, month, week)
        items.append(ReportItem(
            type_code=TYPE_ART,
            type_label=TYPE_LABEL_ART,
            path=p,
            exists=p.exists(),
        ))

    return ReportContext(
        age_code=age,
        month_code=month,
        week_code=week,
        age_label=age_code_to_label(age),
        month_label=month_code_to_label(month),
        week_label=week_code_to_label(week),
        items=items,
    )
