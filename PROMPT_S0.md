# PROMPT_S0.md — Sprint 0: 스캐폴딩 + 라우팅

> 이 프롬프트는 Claude Code 세션에 그대로 붙여넣어 실행할 수 있도록 작성되었습니다.
> 작업 디렉토리에 **CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md**가 함께 있어야 합니다.

---

## 작업 지시 (Claude Code에게 그대로 전달)

당신은 토들러 아트 프로그램 활동 레포트 메이커 프로젝트의 Sprint 0를 수행합니다.

### 0. 사전 읽기 (필수)

작업 시작 전 반드시 아래 순서로 읽고 내재화하세요.

1. `CLAUDE.md` — 프로젝트 전체 컨텍스트 (특히 섹션 5 파일명 매핑, 섹션 9 Do Not Break)
2. `ARCHITECTURE.md` — 아키텍처 결정 기록 (특히 ADR-002 라우팅, ADR-007 pages_local 네이밍)
3. `SPRINT_PLAN.md` — Sprint 0 섹션의 산출물과 인수 조건

읽은 후, 진행하기 전 한 줄 요약을 출력하세요: "Sprint 0 시작: 스캐폴딩 + 라우팅"

---

### 1. 폴더 구조 생성

CLAUDE.md 섹션 3의 구조 그대로 만드세요. `assets/`와 `reports/`는 빈 폴더로 생성 (사용자가 직접 채울 영역).

```
project/
├── app.py
├── pages_local/
│   ├── __init__.py
│   ├── main_page.py
│   └── report_page.py
├── utils/
│   ├── __init__.py
│   ├── mapping.py
│   ├── filename.py
│   ├── state.py
│   └── styling.py
├── assets/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── requirements.txt
└── README.md
```

---

### 2. `requirements.txt`

```
streamlit>=1.30
Pillow>=10.0
```

---

### 3. `utils/mapping.py` — 라벨 ↔ 코드 양방향 매핑

다음 dict와 함수를 정확히 이 키와 값으로 구현하세요.

```python
"""라벨(UI 표시) ↔ 코드(파일명) 양방향 매핑.

CLAUDE.md 섹션 5의 파일명 매핑 규칙과 1:1 일치해야 합니다.
이 파일은 Do Not Break 대상입니다.
"""

# --- 연령 ---
AGE_LABEL_TO_CODE: dict[str, str] = {
    "만1세": "01세",
    "만2세": "02세",
}
AGE_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in AGE_LABEL_TO_CODE.items()}
AGE_LABELS: list[str] = list(AGE_LABEL_TO_CODE.keys())  # 표시 순서 보존
AGE_CODES: list[str] = list(AGE_LABEL_TO_CODE.values())

# --- 표준보육과정 생활주제 (월) ---
# 표시 순서: 3월부터 시작 (보육 1년 기준)
MONTH_LABEL_TO_CODE: dict[str, str] = {
    "3월 어린이집이 좋아요": "03월",
    "4월 봄을 만나요": "04월",
    "5월 우리 가족이 좋아요": "05월",
    "6월 나를 알아요": "06월",
    "7월 여름을 만나요": "07월",
    "8월 동물이랑 놀아요": "08월",
    "9월 여러 가지 탈 것들": "09월",
    "10월 가을과 만나요": "10월",
    "11월 다양한 색과 모양": "11월",
    "12월 겨울과 만나요": "12월",
    "1월 친구들과 놀아요": "01월",
    "2월 함께 자라요": "02월",
}
MONTH_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in MONTH_LABEL_TO_CODE.items()}
MONTH_LABELS: list[str] = list(MONTH_LABEL_TO_CODE.keys())
MONTH_CODES: list[str] = list(MONTH_LABEL_TO_CODE.values())

# --- 주차 ---
WEEK_LABEL_TO_CODE: dict[str, str] = {
    "1주차": "01주",
    "2주차": "02주",
    "3주차": "03주",
    "4주차": "04주",
}
WEEK_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in WEEK_LABEL_TO_CODE.items()}
WEEK_LABELS: list[str] = list(WEEK_LABEL_TO_CODE.keys())
WEEK_CODES: list[str] = list(WEEK_LABEL_TO_CODE.values())

# --- 타입 ---
TYPE_STEAM: str = "스팀월활동"
TYPE_ART: str = "아트활동"


def age_label_to_code(label: str) -> str:
    return AGE_LABEL_TO_CODE[label]


def age_code_to_label(code: str) -> str:
    return AGE_CODE_TO_LABEL[code]


def month_label_to_code(label: str) -> str:
    return MONTH_LABEL_TO_CODE[label]


def month_code_to_label(code: str) -> str:
    return MONTH_CODE_TO_LABEL[code]


def week_label_to_code(label: str) -> str:
    return WEEK_LABEL_TO_CODE[label]


def week_code_to_label(code: str) -> str:
    return WEEK_CODE_TO_LABEL[code]


# --- 검증 헬퍼 ---
def is_valid_age_code(code: str) -> bool:
    return code in AGE_CODE_TO_LABEL


def is_valid_month_code(code: str) -> bool:
    return code in MONTH_CODE_TO_LABEL


def is_valid_week_code(code: str) -> bool:
    return code in WEEK_CODE_TO_LABEL
```

---

### 4. `utils/filename.py` — 리포트 파일명 빌드 + 존재 확인

```python
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
```

---

### 5. `utils/state.py` — session_state 키 상수 + 초기화

```python
"""session_state 키 상수 및 초기화 함수."""
import streamlit as st


# --- 키 상수 (오타 방지) ---
KEY_AGE = "selected_age"
KEY_MONTH = "selected_month"
KEY_WEEK = "selected_week"
KEY_STEAM_FILES = "steam_files"
KEY_ART_FILES = "art_files"
KEY_SHOW_NO_PHOTO_WARNING = "show_no_photo_warning"

# --- 기본값 (CLAUDE.md 섹션 4 원칙 4) ---
DEFAULT_AGE = "01세"
DEFAULT_MONTH = "05월"  # 5월 우리 가족이 좋아요
DEFAULT_WEEK = "03주"


def init_state() -> None:
    """앱 진입 시 한 번 호출. 이미 키가 있으면 덮어쓰지 않는다."""
    st.session_state.setdefault(KEY_AGE, DEFAULT_AGE)
    st.session_state.setdefault(KEY_MONTH, DEFAULT_MONTH)
    st.session_state.setdefault(KEY_WEEK, DEFAULT_WEEK)
    st.session_state.setdefault(KEY_STEAM_FILES, [])
    st.session_state.setdefault(KEY_ART_FILES, [])
    st.session_state.setdefault(KEY_SHOW_NO_PHOTO_WARNING, False)
```

---

### 6. `utils/styling.py` — CSS 인젝션

```python
"""CSS 인젝션. 디자인 토큰은 :root 변수로 집중 관리."""
import streamlit as st


_CSS = """
<style>
:root {
  /* --- 캔버스 --- */
  --canvas-width: 2240px;
  --canvas-height: 1600px;

  /* --- 색상 --- */
  --bg-color: #f2f2f2;
  --primary-color: #5B5FCC;
  --steam-green: #1A8470;
  --button-border: #d0d0d0;
  --button-selected-bg: #5B5FCC;
  --button-selected-fg: #ffffff;
  --button-unselected-bg: #ffffff;
  --button-unselected-fg: #333333;

  /* --- 사이즈 (CLAUDE.md 섹션 7) --- */
  --header-w: 2400px;
  --header-h: 250px;
  --section-title-w: 1020px;
  --section-title-h: 100px;
  --age-btn-w: 500px;     --age-btn-h: 100px;   --age-gap: 20px;
  --topic-btn-w: 330px;   --topic-btn-h: 100px; --topic-gap: 15px;
  --week-btn-w: 240px;    --week-btn-h: 100px;  --week-gap: 20px;
  --upload-w: 1020px;     --upload-h: 400px;
}

/* 사이드바 + 기본 메뉴 숨김 (단일 페이지 라우팅 사용) */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }

/* 기본 배경 */
.stApp { background-color: var(--bg-color); }

/* 메인 컨테이너 패딩 최소화 (커스텀 레이아웃 적용 대비) */
.main .block-container {
  padding-top: 1rem;
  padding-bottom: 1rem;
  max-width: var(--canvas-width);
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
```

---

### 7. `pages_local/main_page.py` — 메인 placeholder

```python
"""메인 페이지 (Sprint 0: placeholder)."""
import streamlit as st
from utils.state import init_state, KEY_AGE, KEY_MONTH, KEY_WEEK


def render() -> None:
    init_state()

    st.markdown("## 메인 화면 (Sprint 0 placeholder)")
    st.write(f"기본 선택값: 연령={st.session_state[KEY_AGE]}, "
             f"월={st.session_state[KEY_MONTH]}, 주차={st.session_state[KEY_WEEK]}")

    # 새 탭 라우팅 테스트용 링크
    test_url = "/?page=report&age=01세&month=05월&week=03주&steam=1&art=1"
    st.markdown(
        f'<a href="{test_url}" target="_blank" '
        f'style="display:inline-block;padding:12px 24px;'
        f'background:var(--primary-color);color:white;border-radius:8px;'
        f'text-decoration:none;font-weight:bold;">'
        f'결과 페이지로 (테스트)</a>',
        unsafe_allow_html=True,
    )
```

---

### 8. `pages_local/report_page.py` — 결과 placeholder

```python
"""결과 페이지 (Sprint 0: placeholder).

session_state에 의존하지 않고 query_params만 읽는다.
새 탭이라 메인의 session_state는 공유되지 않는다.
"""
import streamlit as st
from utils.mapping import (
    is_valid_age_code, is_valid_month_code, is_valid_week_code,
    age_code_to_label, month_code_to_label, week_code_to_label,
)
from utils.filename import steam_path, art_path


def render() -> None:
    qp = st.query_params

    age = qp.get("age", "")
    month = qp.get("month", "")
    week = qp.get("week", "")
    has_steam = qp.get("steam") == "1"
    has_art = qp.get("art") == "1"

    st.markdown("## 결과 화면 (Sprint 0 placeholder)")

    # 검증
    errors = []
    if not is_valid_age_code(age): errors.append(f"age={age!r}")
    if not is_valid_month_code(month): errors.append(f"month={month!r}")
    if not is_valid_week_code(week): errors.append(f"week={week!r}")
    if not (has_steam or has_art): errors.append("steam/art 플래그 없음")

    if errors:
        st.error("쿼리 파라미터 오류: " + ", ".join(errors))
        st.markdown('<a href="/" target="_self">메인으로 돌아가기</a>',
                    unsafe_allow_html=True)
        return

    st.write(f"연령: {age_code_to_label(age)} ({age})")
    st.write(f"월: {month_code_to_label(month)} ({month})")
    st.write(f"주차: {week_code_to_label(week)} ({week})")
    st.write(f"STEAM WALL 업로드: {has_steam}")
    st.write(f"Art 업로드: {has_art}")

    st.divider()
    st.markdown("**조회 예정 파일 (Sprint 2에서 실제 표시)**")
    if has_steam:
        p = steam_path(age, month, week)
        st.code(f"{p.name}  →  {'존재' if p.exists() else '없음'}")
    if has_art:
        p = art_path(age, month, week)
        st.code(f"{p.name}  →  {'존재' if p.exists() else '없음'}")
```

---

### 9. `app.py` — 진입점 + 라우터

```python
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
```

---

### 10. `pages_local/__init__.py` 와 `utils/__init__.py`

빈 파일로 생성.

---

### 11. `README.md`

```markdown
# 토들러 아트 프로그램 활동 레포트 메이커

## 실행

\`\`\`bash
pip install -r requirements.txt
streamlit run app.py
\`\`\`

## 라우팅
- 메인: `http://localhost:8501/`
- 결과: `http://localhost:8501/?page=report&age=01세&month=05월&week=03주&steam=1&art=1`

## 문서
- CLAUDE.md — 프로젝트 컨텍스트
- ARCHITECTURE.md — 아키텍처 결정
- SPRINT_PLAN.md — Sprint 계획
```

---

### 12. 자체 검증 (Sprint 0 인수 조건)

작업 완료 후 아래 명령을 실행하고 결과를 보고하세요.

```bash
streamlit run app.py
```

그리고 다음을 수동 확인 (또는 사용자에게 확인 요청):
- [ ] 사이드바 없이 메인 placeholder 표시
- [ ] 메인의 "결과 페이지로 (테스트)" 링크가 새 탭에서 결과 placeholder를 열음
- [ ] URL을 직접 `/?page=report&age=01세&month=05월&week=03주&steam=1`로 입력 시 결과 placeholder 표시
- [ ] 잘못된 파라미터(예: `age=99세`)일 때 오류 메시지 + 메인 링크 표시
- [ ] 배경색 `#f2f2f2` 적용 확인

마지막으로, 모든 파일 트리를 출력하고 Sprint 0 완료를 보고하세요.

---

### Do Not (이번 Sprint에서 하지 말 것)

- 메인 페이지의 실제 UI 위젯 구현 금지 (Sprint 1에서 다룸)
- 액션 버튼 구현 금지 (Sprint 3)
- assets/와 reports/ 폴더를 임의 콘텐츠로 채우지 말 것 (사용자 제공 영역)
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md 수정 금지 (참조만)
- 파일명 매핑 규칙(`utils/mapping.py`) 임의 변경 금지

---

### 보고 형식

작업 끝에 아래 형식으로 보고하세요.

```
## Sprint 0 완료 보고

### 생성된 파일
- [파일 경로 + 한 줄 설명] × N

### 자체 검증 결과
- [ ] streamlit run app.py 정상 실행
- [ ] 메인 placeholder 표시
- [ ] 새 탭 라우팅 동작
- [ ] mapping.py 양방향 lookup 동작 (간단 테스트 결과 첨부)

### 다음 단계
Sprint 1 — 메인 페이지 UI 완성 준비 완료. PROMPT_S1.md를 사용자에게 요청.
```
