"""토들러 아트 프로그램 활동 레포트 메이커 — 진입점.

라우팅: query_params['page'] = 'main' | 'report'
"""
import streamlit as st

# set_page_config는 다른 모든 streamlit 호출 전에 와야 함
st.set_page_config(
    page_title="토들러 아트 프로그램 활동 레포트 메이커",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styling import inject_css
from pages_local import main_page, report_page


def main() -> None:
    inject_css()
    page = st.query_params.get("page", "main")
    if page == "report":
        report_page.render()
    else:
        main_page.render()


if __name__ == "__main__":
    main()
