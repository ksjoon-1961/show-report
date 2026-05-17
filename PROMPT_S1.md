# PROMPT_S1.md — Sprint 1: 메인 페이지 UI 완성

> 작업 디렉토리에 CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, 그리고 Sprint 0 산출물이 있어야 합니다.

---

## 작업 지시 (Claude Code에게 그대로 전달)

당신은 토들러 아트 프로그램 활동 레포트 메이커 프로젝트의 Sprint 1을 수행합니다.

### 0. 사전 읽기 (필수)

1. `CLAUDE.md` — 전체 컨텍스트 (섹션 4 핵심 원칙, 섹션 7 CSS 변수, 섹션 8 session_state, 섹션 9 Do Not Break)
2. `ARCHITECTURE.md` — **ADR-003 단일선택 버튼, ADR-004 액션 버튼은 보류, ADR-005 CSS 변수**를 집중
3. `SPRINT_PLAN.md` — Sprint 1 섹션의 산출물과 인수 조건 확인
4. 기존 Sprint 0 코드 모두 — 특히 `utils/mapping.py`, `utils/state.py`, `utils/styling.py`의 현재 상태 파악

읽기 후 한 줄 출력: "Sprint 1 시작: 메인 페이지 UI 완성"

---

### 1. 작업 범위 (변경/생성/금지)

**수정할 파일**:
- `utils/styling.py` — CSS 대폭 추가
- `pages_local/main_page.py` — 전면 재작성

**새로 생성할 파일**:
- `utils/url_builder.py` — 결과 페이지 URL 빌드
- `utils/asset_helper.py` — 이미지 with text fallback
- `BEHAVIOR.md` — 동작 명세 (초판)

**절대 수정 금지**:
- `app.py`
- `pages_local/report_page.py`
- `utils/mapping.py`
- `utils/filename.py`
- `utils/state.py` (이미 모든 키 정의됨)
- `requirements.txt`
- 모든 .md 문서 (CLAUDE/ARCHITECTURE/SPRINT_PLAN/PROMPT_S0/PROMPT_S1)

---

### 2. `utils/url_builder.py` (신규)

```python
"""결과 페이지 URL 빌드.

새 탭으로 결과 페이지를 열 때 사용하는 쿼리 파라미터 URL을 생성한다.
한글 코드(01세 등)는 URL 인코딩한다.
"""
from urllib.parse import quote


def build_report_url(age_code: str, month_code: str, week_code: str,
                     has_steam: bool, has_art: bool) -> str:
    """결과 페이지로 가는 상대 URL을 반환.
    
    예: ?page=report&age=01%EC%84%B8&month=05%EC%9B%94&week=03%EC%A3%BC&steam=1&art=1
    """
    params = [
        ("page", "report"),
        ("age", age_code),
        ("month", month_code),
        ("week", week_code),
    ]
    if has_steam:
        params.append(("steam", "1"))
    if has_art:
        params.append(("art", "1"))
    
    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    return f"?{query}"
```

---

### 3. `utils/asset_helper.py` (신규)

```python
"""assets/ 폴더의 이미지를 HTML img 태그로 반환.

이미지 파일이 없으면 텍스트 fallback을 반환한다.
앱이 죽지 않도록 보장하기 위함 (Do Not Break #7과 같은 정신).
"""
import base64
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _to_data_uri(path: Path) -> str:
    """Streamlit의 정적 서빙 제약을 피하기 위해 data URI로 인라인."""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def img_or_text(filename: str, fallback_text: str,
                width: str = "auto", height: str = "auto",
                css_class: str = "") -> str:
    """이미지가 있으면 <img>, 없으면 fallback 텍스트 HTML 반환.
    
    width/height는 CSS 값 (예: "1020px", "100%", "auto").
    """
    path = ASSETS_DIR / filename
    cls_attr = f' class="{css_class}"' if css_class else ""
    
    if path.exists():
        src = _to_data_uri(path)
        return (f'<img src="{src}" '
                f'style="width:{width};height:{height};object-fit:contain;"'
                f'{cls_attr} alt="{fallback_text}" />')
    else:
        return (f'<div style="width:{width};height:{height};'
                f'display:flex;align-items:center;justify-content:left;'
                f'font-size:24px;font-weight:bold;color:#333;"'
                f'{cls_attr}>{fallback_text}</div>')
```

---

### 4. `utils/styling.py` (전면 갱신)

기존 파일을 다음 내용으로 **완전히 교체**하세요.

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

  /* --- 사이즈 --- */
  --header-w: 2400px;
  --header-h: 250px;
  --section-title-w: 1020px;
  --section-title-h: 100px;
  --age-btn-w: 500px;     --age-btn-h: 100px;   --age-gap: 20px;
  --topic-btn-w: 330px;   --topic-btn-h: 100px; --topic-gap: 15px;
  --week-btn-w: 240px;    --week-btn-h: 100px;  --week-gap: 20px;
  --upload-w: 1020px;     --upload-h: 400px;
}

/* 사이드바 + 기본 메뉴 숨김 */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }

/* 기본 배경 */
.stApp { background-color: var(--bg-color); }

/* 메인 컨테이너 */
.main .block-container {
  padding-top: 1rem;
  padding-bottom: 2rem;
  max-width: var(--canvas-width);
}

/* --- 헤더 영역 --- */
.header-area {
  width: 100%;
  margin-bottom: 30px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}
.header-area img {
  max-width: 100%;
  height: auto;
}

/* --- 섹션 타이틀 --- */
.section-title {
  margin: 25px 0 15px;
  height: 60px;
  display: flex;
  align-items: center;
}
.section-title img { height: 60px; }

/* --- 선택 카드 버튼 (Streamlit st.button) --- */
[data-testid="stButton"] > button {
  height: var(--age-btn-h) !important;
  border-radius: 12px !important;
  font-size: 18px !important;
  font-weight: 600 !important;
  transition: all 0.15s ease;
}

[data-testid="stButton"] > button[kind="primary"] {
  background-color: var(--button-selected-bg) !important;
  color: var(--button-selected-fg) !important;
  border: 2px solid var(--button-selected-bg) !important;
}

[data-testid="stButton"] > button[kind="secondary"] {
  background-color: var(--button-unselected-bg) !important;
  color: var(--button-unselected-fg) !important;
  border: 1px solid var(--button-border) !important;
}

[data-testid="stButton"] > button:hover {
  border-color: var(--primary-color) !important;
  transform: translateY(-1px);
}

/* --- 컬럼 갭 미세조정 --- */
[data-testid="stHorizontalBlock"] {
  gap: 15px;
}

/* --- 파일 업로더 --- */
[data-testid="stFileUploader"] {
  margin-bottom: 25px;
}
[data-testid="stFileUploader"] section {
  height: 400px !important;
  border: 2px dashed #c0c0c0 !important;
  border-radius: 16px !important;
  background-color: #ffffff !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
[data-testid="stFileUploader"] section > button {
  display: none !important;  /* "Browse files" 버튼 숨김 → 드래그 강조 */
}
[data-testid="stFileUploader"] section > div > small {
  font-size: 18px !important;
  color: #888 !important;
}
[data-testid="stFileUploader"] section::after {
  content: "";
}

/* --- 생성 버튼 (HTML 앵커 / 비활성 버튼 공통 외형) --- */
.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1400px;
  margin: 40px auto 20px;
  padding: 28px;
  background: var(--primary-color);
  color: white !important;
  text-align: center;
  font-size: 28px;
  font-weight: 800;
  border-radius: 16px;
  text-decoration: none !important;
  box-shadow: 0 4px 12px rgba(91, 95, 204, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}
.generate-btn:hover {
  background: #4a4eb8;
  transform: translateY(-2px);
}
.generate-btn-icon {
  display: inline-block;
  width: 50px; height: 50px;
  border-radius: 50%;
  background: #1a1a1a;
  color: white;
  text-align: center;
  line-height: 50px;
  margin-right: 20px;
  font-size: 24px;
}

/* 비활성 상태의 생성 버튼 (st.button로 렌더링되는 경우) */
[data-testid="stButton"] > button[data-generate-disabled="true"] {
  background-color: var(--primary-color) !important;
  color: white !important;
  border: none !important;
  font-size: 28px !important;
  font-weight: 800 !important;
  height: 100px !important;
  border-radius: 16px !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
```

---

### 5. `pages_local/main_page.py` (전면 재작성)

기존 placeholder를 다음으로 **완전히 교체**하세요.

```python
"""메인 페이지 — 연령/월/주차 선택 + 사진 업로드 + 결과 생성."""
import streamlit as st

from utils.state import (
    init_state,
    KEY_AGE, KEY_MONTH, KEY_WEEK,
    KEY_STEAM_FILES, KEY_ART_FILES,
    KEY_SHOW_NO_PHOTO_WARNING,
)
from utils.mapping import (
    AGE_LABELS, MONTH_LABELS, WEEK_LABELS,
    age_label_to_code, month_label_to_code, week_label_to_code,
)
from utils.url_builder import build_report_url
from utils.asset_helper import img_or_text


# ============================================================
# 섹션 렌더러
# ============================================================

def _render_header() -> None:
    """상단 헤더 (STEAM WALL 타이틀)."""
    html = img_or_text(
        "header.png",
        "STEAM WALL 토들러 아트 프로그램 활동 레포트 메이커",
        width="100%", height="180px",
    )
    st.markdown(f'<div class="header-area">{html}</div>',
                unsafe_allow_html=True)


def _render_section_title(filename: str, fallback: str) -> None:
    html = img_or_text(filename, fallback, width="auto", height="60px")
    st.markdown(f'<div class="section-title">{html}</div>',
                unsafe_allow_html=True)


def _render_age_group() -> None:
    """수업 연령: 만1세 / 만2세 (단일 선택, 2개 한 행)."""
    _render_section_title("age_icon.png", "👧👦 수업 연령")
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
    """표준보육과정 생활주제: 12개 (3개 × 4행, 단일 선택)."""
    _render_section_title("topic_icon.png", "👨‍👩‍👧 표준보육과정 생활 주제")
    for row_start in range(0, 12, 3):
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
    """수업 주차: 1주차~4주차 (단일 선택, 4개 한 행)."""
    _render_section_title("week_icon.png", "📅 수업 주차")
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


def _render_steam_upload() -> None:
    """STEAM WALL 활동 사진 업로드."""
    _render_section_title("camera_icon_steam.png",
                          "📷 STEAM WALL 활동 사진 업로드")
    files = st.file_uploader(
        "STEAM WALL", type=["png", "jpg", "jpeg"],
        accept_multiple_files=True, key="steam_uploader",
        label_visibility="collapsed",
    )
    st.session_state[KEY_STEAM_FILES] = files or []


def _render_art_upload() -> None:
    """아트 활동 사진 업로드."""
    _render_section_title("camera_icon_art.png",
                          "📷 아트 활동 사진 업로드")
    files = st.file_uploader(
        "Art", type=["png", "jpg", "jpeg"],
        accept_multiple_files=True, key="art_uploader",
        label_visibility="collapsed",
    )
    st.session_state[KEY_ART_FILES] = files or []


# ============================================================
# 경고 다이얼로그
# ============================================================

@st.dialog("알림")
def _show_no_photo_warning() -> None:
    st.markdown("### 📷 사진을 입력하세요")
    st.write("STEAM WALL 또는 아트 활동 사진을 최소 1장 업로드해주세요.")
    if st.button("확인", key="warning_ok", use_container_width=True):
        st.session_state[KEY_SHOW_NO_PHOTO_WARNING] = False
        st.rerun()


# ============================================================
# 생성 버튼
# ============================================================

def _render_generate_button() -> None:
    """업로드 상태에 따라 두 가지 모드:
    - 업로드 있음: HTML 앵커 (새 탭 라우팅, target="_blank")
    - 업로드 없음: st.button (클릭 시 경고 팝업)
    """
    has_steam = bool(st.session_state[KEY_STEAM_FILES])
    has_art = bool(st.session_state[KEY_ART_FILES])
    can_proceed = has_steam or has_art

    if can_proceed:
        url = build_report_url(
            st.session_state[KEY_AGE],
            st.session_state[KEY_MONTH],
            st.session_state[KEY_WEEK],
            has_steam, has_art,
        )
        st.markdown(
            f'<a href="{url}" target="_blank" class="generate-btn">'
            f'<span class="generate-btn-icon">▶</span>'
            f'토들러 아트 프로그램 활동 레포트 생성'
            f'</a>',
            unsafe_allow_html=True,
        )
    else:
        # st.button을 같은 외형으로 보이도록 CSS 클래스 부여
        st.markdown(
            '<div style="margin-top:40px;"></div>', unsafe_allow_html=True,
        )
        if st.button(
            "▶  토들러 아트 프로그램 활동 레포트 생성",
            key="generate_btn_disabled",
            type="primary",
            use_container_width=True,
        ):
            st.session_state[KEY_SHOW_NO_PHOTO_WARNING] = True
            st.rerun()


# ============================================================
# 진입점
# ============================================================

def render() -> None:
    init_state()

    # 경고 다이얼로그 (조건부)
    if st.session_state.get(KEY_SHOW_NO_PHOTO_WARNING):
        _show_no_photo_warning()

    # 헤더
    _render_header()

    # 본문: 좌우 2컬럼
    left, right = st.columns([1, 1], gap="large")

    with left:
        _render_age_group()
        _render_month_group()
        _render_week_group()

    with right:
        _render_steam_upload()
        _render_art_upload()

    # 생성 버튼 (전체 폭)
    _render_generate_button()
```

---

### 6. `BEHAVIOR.md` (신규)

```markdown
# BEHAVIOR.md

> 회귀 테스트용 동작 명세. 각 Sprint 종료 시 추가됨.

---

## Sprint 0 — 스캐폴딩 + 라우팅 (Done)

- 메인 진입(`/`) 시 사이드바 없는 placeholder 표시
- `/?page=report&...` URL 직접 입력 시 결과 placeholder 표시
- 잘못된 query_params → 오류 메시지 + 메인 링크
- 매핑 양방향 lookup: 연령 2개, 월 12개, 주차 4개
- 기본값: 01세 / 05월 / 03주

---

## Sprint 1 — 메인 페이지 UI 완성 (Done)

### 첫 진입 상태
- 헤더 영역에 assets/header.png 표시 (없으면 텍스트 fallback)
- 만1세가 보라색(선택), 만2세가 흰색(비선택)
- "5월 우리 가족이 좋아요"가 보라색(선택), 나머지 11개 월 항목은 흰색
- 3주차가 보라색(선택), 나머지 3개 주차는 흰색
- 두 업로드 영역 모두 비어 있음
- 하단 "토들러 아트 프로그램 활동 레포트 생성" 버튼 보임

### 단일 선택 동작
- 연령 그룹: 만2세 클릭 → 만2세만 보라색, 만1세 자동 흰색 전환
- 월 그룹: 임의 항목 클릭 시 해당 항목만 선택, 다른 11개 자동 해제
- 주차 그룹: 임의 주차 클릭 시 해당 주차만 선택, 다른 3개 자동 해제
- 동일 그룹 내 동시 2개 선택 상태는 절대 발생하지 않음

### 업로드 동작
- 각 업로드 영역에 jpg/png/jpeg 파일 드래그앤드롭 가능
- 멀티 파일 업로드 지원
- 업로드된 파일은 session_state[KEY_STEAM_FILES] / [KEY_ART_FILES]에 보관
- 다른 위젯 클릭으로 rerun 발생해도 업로드 파일 유지

### 생성 버튼 동작
- 양쪽 업로드 모두 비어 있는 상태에서 클릭:
  - st.dialog로 "사진을 입력하세요" 경고 다이얼로그 표시
  - "확인" 클릭 시 다이얼로그 닫힘
- 한쪽이라도 업로드된 상태에서 클릭:
  - 새 탭으로 결과 페이지 열림
  - URL은 build_report_url 규칙대로 구성됨
  - URL의 steam=1, art=1 플래그가 실제 업로드 여부와 일치

### 시각 일관성
- 배경색 #f2f2f2
- 선택 버튼: 보라색 (#5B5FCC) + 흰 글자
- 비선택 버튼: 흰색 + 검정 글자 + 회색 테두리
- 사이드바 / Streamlit 기본 메뉴 / Streamlit 헤더 모두 숨김
```

---

### 7. 자체 검증

다음을 차례로 실행하고 결과를 보고에 포함:

```bash
# 모듈 import 정상
python -c "from pages_local.main_page import render; print('main_page OK')"
python -c "from utils.url_builder import build_report_url; print('url_builder OK')"
python -c "from utils.asset_helper import img_or_text; print('asset_helper OK')"

# url_builder 케이스 테스트
python -c "from utils.url_builder import build_report_url; print(build_report_url('01세','05월','03주',True,True))"
# 기대: ?page=report&age=01%EC%84%B8&month=05%EC%9B%94&week=03%EC%A3%BC&steam=1&art=1

python -c "from utils.url_builder import build_report_url; print(build_report_url('02세','07월','02주',False,True))"
# 기대: ?page=report&age=02%EC%84%B8&month=07%EC%9B%94&week=02%EC%A3%BC&art=1

# asset_helper fallback (assets/ 비어있는 상태)
python -c "from utils.asset_helper import img_or_text; print('IMG' if 'img' in img_or_text('nonexist.png','테스트') else 'TEXT' if 'div' in img_or_text('nonexist.png','테스트') else 'UNKNOWN')"
# 기대: TEXT
```

이어서 Streamlit 부팅 테스트:

```bash
# Windows
start /B streamlit run app.py --server.headless true --server.port 8501
# 5초 대기 후
curl -s -o NUL -w "%%{http_code}" http://localhost:8501
# 기대: 200
# 그 후 프로세스 종료
```

---

### 8. Do Not

- `st.radio`, `st.checkbox`, `st.selectbox` 사용 금지 (ADR-003에 따라 `st.button` + `type="primary"|"secondary"` 사용)
- 새 탭 라우팅 외의 페이지 전환 방식 사용 금지
- 단일 선택 보장: 한 그룹 내 동시 2개 선택 가능성 코드 절대 작성 금지
- 액션 버튼(저장/인쇄/메인/공유) 구현 금지 (Sprint 3 범위)
- 결과 페이지(`report_page.py`) 수정 금지 (Sprint 2 범위)
- 매핑 dict 추가/수정 금지
- 한글이 깨질 수 있는 처리(`encode('ascii')` 등) 금지

---

### 9. 보고 형식

```
## Sprint 1 완료 보고

### 수정/생성된 파일
- [파일 경로 + 한 줄 설명] × N

### 자체 검증 결과
- [ ] 모듈 import: main_page / url_builder / asset_helper
- [ ] url_builder 케이스 1 (양쪽 업로드)
- [ ] url_builder 케이스 2 (Art만 업로드)
- [ ] asset_helper fallback 동작
- [ ] Streamlit HTTP 200

### 알려진 한계
- assets/ 폴더에 이미지가 비어 있어 텍스트 fallback이 표시됨
  → 사용자가 7개 이미지를 배치하면 자동으로 이미지 표시로 전환됨
- 시각적 디자인 미세조정(여백, 폰트 크기 등)은 사용자 검수 후 반영 가능

### 사용자 수동 확인 요청 항목
1. `streamlit run app.py` 실행 후 첫 진입 시 기본값(만1세 / 5월 우리가족이 좋아요 / 3주차)이 보라색으로 표시되는지
2. 동일 그룹 내 다른 옵션 클릭 시 단일 선택이 유지되는지
3. 양쪽 업로드 없이 생성 클릭 시 경고 다이얼로그가 뜨는지
4. 한쪽 업로드 후 생성 클릭 시 새 탭이 열리고 올바른 query_params를 가지는지
5. assets/ 폴더에 이미지를 배치하면 fallback 텍스트 대신 이미지가 표시되는지

### 다음 단계
Sprint 2 — 결과 페이지 lookup + 표시 준비 완료. PROMPT_S2.md를 사용자에게 요청.
```
