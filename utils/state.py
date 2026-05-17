"""session_state 키 상수 및 초기화 함수."""
import streamlit as st


# --- 키 상수 ---
KEY_AGE   = "selected_age"
KEY_MONTH = "selected_month"
KEY_WEEK  = "selected_week"
KEY_STEAM_IMAGES = "steam_images"   # dict {filename: bytes}
KEY_ART_IMAGES   = "art_images"     # dict {filename: bytes}
KEY_STEAM_NONCE  = "steam_nonce"    # STEAM 업로더 key 회전용
KEY_ART_NONCE    = "art_nonce"      # Art 업로더 key 회전용

# --- 기본값 ---
DEFAULT_AGE   = "01세"
DEFAULT_MONTH = "05월"
DEFAULT_WEEK  = "03주"


def init_state() -> None:
    """앱 진입 시 한 번 호출. 이미 키가 있으면 덮어쓰지 않는다."""
    st.session_state.setdefault(KEY_AGE,   DEFAULT_AGE)
    st.session_state.setdefault(KEY_MONTH, DEFAULT_MONTH)
    st.session_state.setdefault(KEY_WEEK,  DEFAULT_WEEK)
    st.session_state.setdefault(KEY_STEAM_IMAGES, {})
    st.session_state.setdefault(KEY_ART_IMAGES,   {})
    st.session_state.setdefault(KEY_STEAM_NONCE, 0)
    st.session_state.setdefault(KEY_ART_NONCE,   0)
