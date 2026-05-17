"""결과 페이지 — query_params 기반 lookup + 표시.

session_state에 의존하지 않는다. 새 탭이라 메인 페이지 state는 공유되지 않음.
모든 정보는 st.query_params에서 읽고 utils.report_loader가 검증/조립.
"""
import base64
import streamlit as st
import streamlit.components.v1 as components

from utils.report_loader import (
    load_from_query_params,
    QueryError, ReportItem,
)
from utils.mapping import TYPE_STEAM
from utils.action_buttons import build_combined_action_buttons_html


# ============================================================
# 헬퍼
# ============================================================

def _render_query_error(err: QueryError) -> None:
    st.markdown(
        f'<div class="report-error-box">'
        f'<h3>⚠️ 잘못된 요청입니다</h3>'
        f'<p>{err.message}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<a href="/" target="_self" class="back-to-main-link">'
        '← 메인 화면으로 돌아가기</a>',
        unsafe_allow_html=True,
    )


def _build_box_inner(item: "ReportItem | None") -> str:
    """박스 내부 HTML 반환 — 이미지 또는 미생성 메시지."""
    if item is not None and item.exists:
        mime = "image/jpeg" if item.path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        b64 = base64.b64encode(item.path.read_bytes()).decode()
        return (
            f'<img src="data:{mime};base64,{b64}"'
            f' style="width:100%;height:auto;display:block;border-radius:6px;">'
        )
    return '<p class="report-empty-msg">해당 레포트는<br>생성되지 않았습니다</p>'


# ============================================================
# 진입점
# ============================================================

def render() -> None:
    result = load_from_query_params(st.query_params)

    if isinstance(result, QueryError):
        _render_query_error(result)
        return

    steam_item = next((i for i in result.items if i.type_code == TYPE_STEAM), None)
    art_item   = next((i for i in result.items if i.type_code != TYPE_STEAM), None)

    # 두 박스를 하나의 flex 컨테이너로 렌더링
    # align-items:stretch → 이미지 박스 높이에 빈 박스가 자동으로 맞춰짐
    steam_inner = _build_box_inner(steam_item)
    art_inner   = _build_box_inner(art_item)

    ROW_STYLE = (
        "display:flex;"
        "gap:20px;"
        "width:75%;"
        "margin:8px auto 20px;"
        "align-items:stretch;"
        "box-sizing:border-box;"
    )
    BOX_STYLE = (
        "flex:1;"
        "border:1.5px solid rgba(49,51,63,0.3);"
        "border-radius:12px;"
        "padding:10px;"
        "background:white;"
        "display:flex;"
        "flex-direction:column;"
        "align-items:center;"
        "justify-content:center;"
        "box-sizing:border-box;"
        "overflow:hidden;"
        "min-width:0;"
    )
    st.markdown(
        f'<div style="{ROW_STYLE}">'
        f'<div style="{BOX_STYLE}">{steam_inner}</div>'
        f'<div style="{BOX_STYLE}">{art_inner}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 공통 4개 액션 버튼 — 크기 변경 없음
    existing_paths = [i.path for i in result.items if i.exists]
    html = build_combined_action_buttons_html(existing_paths)
    components.html(html, height=100)

    if not result.has_any_existing:
        st.markdown(
            '<div class="report-info-banner">'
            '💡 선택하신 조건의 레포트가 아직 준비되지 않았습니다. '
            '<a href="/" target="_self">메인 화면으로 돌아가기</a>'
            '</div>',
            unsafe_allow_html=True,
        )
