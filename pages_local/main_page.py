"""메인 페이지 — 연령/월/주차 선택 + 사진 업로드 + 결과 생성."""
import streamlit as st

from utils.state import (
    init_state,
    KEY_AGE, KEY_MONTH, KEY_WEEK,
    KEY_STEAM_IMAGES, KEY_ART_IMAGES,
    KEY_STEAM_NONCE, KEY_ART_NONCE,
)
from utils.mapping import (
    AGE_LABELS, MONTH_LABELS, WEEK_LABELS,
    age_label_to_code, month_label_to_code, week_label_to_code,
)
from utils.url_builder import build_report_url
from utils.asset_helper import img_or_text

_GALLERY_HEIGHT = 215
_GALLERY_THUMB_COLS = 3   # 갤러리 영역 내 썸네일 열 수


# ============================================================
# 섹션 렌더러
# ============================================================

def _render_header() -> None:
    html = img_or_text(
        "토들러아트 인터페이스_최상단 제목.png",
        "STEAM WALL 토들러 아트 프로그램 활동 레포트 메이커",
        width="100%", height="auto",
    )
    st.markdown(f'<div class="header-area">{html}</div>', unsafe_allow_html=True)


def _render_section_title(filename: str, fallback: str, extra_style: str = "") -> None:
    html = img_or_text(filename, fallback, width="100%", height="auto")
    style_attr = f' style="{extra_style}"' if extra_style else ""
    st.markdown(f'<div class="section-title"{style_attr}>{html}</div>', unsafe_allow_html=True)


def _render_age_group() -> None:
    _render_section_title("토들러아트 인터페이스_1.png", "👧👦 수업 연령")
    cols = st.columns(2)
    for i, label in enumerate(AGE_LABELS):
        code = age_label_to_code(label)
        is_sel = (st.session_state[KEY_AGE] == code)
        with cols[i]:
            if st.button(
                label, key=f"age_{code}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
            ):
                st.session_state[KEY_AGE] = code
                st.rerun()


def _render_month_group() -> None:
    _render_section_title("토들러아트 인터페이스_2.png", "👨‍👩‍👧 표준보육과정 생활 주제")
    for row_start in range(0, 12, 3):
        if row_start > 0:
            st.markdown('<div class="month-row-gap"></div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for j, label in enumerate(MONTH_LABELS[row_start:row_start + 3]):
            code = month_label_to_code(label)
            is_sel = (st.session_state[KEY_MONTH] == code)
            with cols[j]:
                if st.button(
                    label, key=f"month_{code}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                ):
                    st.session_state[KEY_MONTH] = code
                    st.rerun()


def _render_week_group() -> None:
    _render_section_title("토들러아트 인터페이스_3.png", "📅 수업 주차")
    cols = st.columns(4)
    for i, label in enumerate(WEEK_LABELS):
        code = week_label_to_code(label)
        is_sel = (st.session_state[KEY_WEEK] == code)
        with cols[i]:
            if st.button(
                label, key=f"week_{code}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
            ):
                st.session_state[KEY_WEEK] = code
                st.rerun()


def _render_upload_section(
    title_file: str,
    title_fallback: str,
    state_key: str,
    nonce_key: str,
    uploader_label: str,
) -> None:
    """공통 업로드 섹션: 타이틀 + 갤러리 박스(스크롤) + 드롭존 박스(독립).

    두 박스는 완전히 분리된다. 갤러리만 스크롤, 드롭존은 항상 고정 형태.
    """
    _render_section_title(
        title_file, title_fallback,
        extra_style="margin-top: 20px; margin-bottom: 0; padding-bottom: 0; line-height: 1.3;",
    )
    st.markdown('<hr class="gallery-top-line">', unsafe_allow_html=True)
    col_gallery, col_drop = st.columns([3, 1])

    with col_gallery:
        with st.container(height=_GALLERY_HEIGHT, border=True):
            images: dict = st.session_state[state_key]
            if not images:
                st.caption("이미지를 업로드해 주세요")
            else:
                g_cols = st.columns(_GALLERY_THUMB_COLS)
                for idx, (name, data) in enumerate(images.items()):
                    with g_cols[idx % _GALLERY_THUMB_COLS]:
                        st.image(data, use_container_width=True)
                        if st.button("✕", key=f"del_{state_key}_{name}"):
                            del st.session_state[state_key][name]
                            st.rerun()

    with col_drop:
        nonce = st.session_state[nonce_key]
        new_files = st.file_uploader(
            uploader_label,
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=f"{state_key}_up_{nonce}",
            label_visibility="collapsed",
        )

        if new_files:
            added = False
            for f in new_files:
                if f.name not in st.session_state[state_key]:
                    st.session_state[state_key][f.name] = f.getvalue()
                    added = True
            if added:
                st.session_state[nonce_key] += 1
                st.rerun()


# ============================================================
# 생성 버튼
# ============================================================

def _render_generate_button() -> None:
    has_steam = bool(st.session_state[KEY_STEAM_IMAGES])
    has_art   = bool(st.session_state[KEY_ART_IMAGES])
    can_proceed = has_steam or has_art

    img_html = img_or_text(
        "토들러아트생성_1200x130px.png",
        "토들러 아트 프로그램 활동 레포트 생성",
        width="100%", height="auto",
    )

    if can_proceed:
        url = build_report_url(
            st.session_state[KEY_AGE],
            st.session_state[KEY_MONTH],
            st.session_state[KEY_WEEK],
            has_steam, has_art,
        )
        st.markdown(
            f'<a href="{url}" class="generate-img-link" '
            f'onclick="window.open(this.href,\'_blank\');return false;">{img_html}</a>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="generate-img-disabled">{img_html}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# 진입점
# ============================================================

def render() -> None:
    init_state()
    _render_header()

    left, _spacer, right = st.columns([1, 0.1, 1], gap="small")

    with left:
        _render_age_group()
        _render_month_group()
        _render_week_group()

    with right:
        _render_upload_section(
            "토들러아트 인터페이스_4.png",
            "📷 STEAM WALL 활동 사진 업로드",
            KEY_STEAM_IMAGES,
            KEY_STEAM_NONCE,
            "STEAM WALL 사진",
        )
        st.markdown('<div class="art-section-gap"></div>', unsafe_allow_html=True)
        _render_upload_section(
            "토들러아트 인터페이스_5.png",
            "📷 아트 활동 사진 업로드",
            KEY_ART_IMAGES,
            KEY_ART_NONCE,
            "아트 활동 사진",
        )

    _render_generate_button()
