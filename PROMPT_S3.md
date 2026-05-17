# PROMPT_S3.md — Sprint 3: 액션 버튼 + 폴리싱

> 이번 Sprint로 MVP가 완성됩니다. Sprint 0·1·2 산출물이 모두 존재해야 합니다.

---

## 작업 지시 (Claude Code에게 그대로 전달)

당신은 토들러 아트 프로그램 활동 레포트 메이커 프로젝트의 Sprint 3을 수행합니다. 이번 Sprint로 MVP가 완성됩니다.

### 0. 사전 읽기 (필수)

1. `CLAUDE.md` — 전체. 특히 섹션 9 Do Not Break 11개 항목 모두
2. `ARCHITECTURE.md` — **ADR-004 액션 버튼은 HTML/JS 커스텀 블록** 정확히 따름
3. `SPRINT_PLAN.md` — Sprint 3 산출물 + 인수 조건
4. 기존 코드 — `pages_local/report_page.py`(특히 `_render_action_placeholder`), `utils/styling.py`, `utils/asset_helper.py`(`ASSETS_DIR`)
5. `BEHAVIOR.md` — Sprint 0·1·2 섹션 모두 (회귀 시 깨지면 안 되는 동작)

읽기 후 한 줄 출력: "Sprint 3 시작: 액션 버튼 + 폴리싱"

---

### 1. 작업 범위

**수정할 파일**:
- `pages_local/report_page.py` — placeholder 함수 호출을 실제 액션 버튼 함수 호출로 교체
- `utils/styling.py` — `@media print` 블록 추가 (기존 CSS 보존)
- `BEHAVIOR.md` — Sprint 3 섹션 추가 + MVP 완료 회고 섹션 추가

**새로 생성할 파일**:
- `utils/action_buttons.py` — 4개 액션 버튼 HTML/JS 블록 빌더

**절대 수정 금지**:
- `app.py`
- `pages_local/main_page.py`
- `utils/{mapping,filename,state,url_builder,asset_helper,report_loader}.py`
- `requirements.txt`
- 모든 .md 문서 (CLAUDE/ARCHITECTURE/SPRINT_PLAN/PROMPT_S0~S3)

---

### 2. `utils/action_buttons.py` (신규)

```python
"""결과 페이지의 4개 액션 버튼 (저장/인쇄/메인/공유) HTML/JS 빌더.

각 리포트 이미지마다 독립된 iframe(st.components.v1.html)으로 렌더링된다.
iframe 내부에서 window.parent를 통해 부모 페이지의 navigation/print/share를 제어한다.
ADR-004 준수.
"""
import base64
import json
from pathlib import Path

from utils.asset_helper import ASSETS_DIR


# 액션 → assets/ 아이콘 파일명 매핑
_ICON_FILES = {
    "save": "btn_save.png",
    "print": "btn_print.png",
    "main": "btn_main.png",
    "share": "btn_share.png",
}

# 액션 → 한글 라벨
_LABELS = {
    "save": "저장",
    "print": "인쇄",
    "main": "메인",
    "share": "공유",
}


def _data_uri(path: Path) -> str:
    """이미지 파일 → data URI 변환. 파일 없으면 빈 문자열."""
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix, "application/octet-stream")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _button_inner(action: str) -> str:
    """버튼 내부 콘텐츠. 아이콘 파일 있으면 이미지, 없으면 텍스트 fallback."""
    icon_path = ASSETS_DIR / _ICON_FILES[action]
    label = _LABELS[action]
    if icon_path.exists():
        uri = _data_uri(icon_path)
        return (
            f'<img src="{uri}" alt="{label}" />'
            f'<span class="action-btn-label">{label}</span>'
        )
    return f'<span class="action-btn-fallback">{label}</span>'


# CSS는 iframe 내부에서 독립적으로 정의 (parent CSS 변수 접근 불가)
_IFRAME_CSS = """
html, body {
    margin: 0; padding: 0; background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif;
}
.action-buttons-row {
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 16px 0;
}
.action-btn-real {
    width: 140px;
    height: 100px;
    background: #ffffff;
    border: 2px solid #d0d0d0;
    border-radius: 14px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
    padding: 8px;
    font-family: inherit;
}
.action-btn-real:hover {
    border-color: #5B5FCC;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(91, 95, 204, 0.2);
}
.action-btn-real:active { transform: translateY(0); }
.action-btn-real img {
    width: 48px; height: 48px;
    object-fit: contain; margin-bottom: 6px;
}
.action-btn-label {
    font-size: 14px; font-weight: 600; color: #333;
}
.action-btn-fallback {
    font-size: 20px; font-weight: 700; color: #333;
}
"""


def build_action_buttons_html(report_jpg_path: Path) -> str:
    """단일 리포트 이미지에 딸린 4개 버튼 블록 HTML 반환.
    
    st.components.v1.html(..., height=140)로 렌더링할 것.
    """
    img_uri = _data_uri(report_jpg_path)
    filename = report_jpg_path.name

    js = f"""
const IMG_URI = {json.dumps(img_uri)};
const FILENAME = {json.dumps(filename)};

function getParentURL() {{
    try {{ return window.parent.location.href; }}
    catch(e) {{ return window.location.href; }}
}}

function doSave() {{
    if (!IMG_URI) {{
        alert('저장할 이미지가 없습니다.');
        return;
    }}
    const a = document.createElement('a');
    a.href = IMG_URI;
    a.download = FILENAME;
    document.body.appendChild(a);
    a.click();
    a.remove();
}}

function doPrint() {{
    try {{ window.parent.print(); }}
    catch(e) {{ window.print(); }}
}}

function doMain() {{
    try {{ window.parent.location.href = '/'; }}
    catch(e) {{
        try {{ window.top.location.href = '/'; }}
        catch(e2) {{ window.location.href = '/'; }}
    }}
}}

async function doShare() {{
    const url = getParentURL();
    const title = '토들러 아트 활동 레포트';
    if (navigator.share) {{
        try {{
            await navigator.share({{title: title, url: url}});
            return;
        }} catch(e) {{
            if (e.name === 'AbortError') return;
        }}
    }}
    try {{
        await navigator.clipboard.writeText(url);
        alert('URL이 클립보드에 복사되었습니다.');
    }} catch(e) {{
        prompt('이 URL을 복사해주세요:', url);
    }}
}}
"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{_IFRAME_CSS}</style>
</head>
<body>
<div class="action-buttons-row">
<button class="action-btn-real" onclick="doSave()" aria-label="저장">{_button_inner("save")}</button>
<button class="action-btn-real" onclick="doPrint()" aria-label="인쇄">{_button_inner("print")}</button>
<button class="action-btn-real" onclick="doMain()" aria-label="메인">{_button_inner("main")}</button>
<button class="action-btn-real" onclick="doShare()" aria-label="공유">{_button_inner("share")}</button>
</div>
<script>{js}</script>
</body>
</html>"""
```

---

### 3. `pages_local/report_page.py` (부분 수정)

기존 파일에서 다음 두 가지만 수정합니다.

**(a) Import 추가** — 파일 상단에 다음을 추가:
```python
import streamlit.components.v1 as components

from utils.action_buttons import build_action_buttons_html
```

**(b) `_render_action_placeholder()` 함수를 다음으로 교체**:

```python
def _render_action_buttons(report_jpg_path) -> None:
    """4개 액션 버튼 (저장/인쇄/메인/공유).
    
    iframe(components.html)으로 격리된 HTML/JS 블록.
    height는 버튼(100px) + 패딩(16px*2) + 여유분 = 140.
    """
    html = build_action_buttons_html(report_jpg_path)
    components.html(html, height=140)
```

**(c) `_render_report_item()` 함수 내부 호출 변경**:

기존:
```python
        _render_action_placeholder()
```

→ 변경:
```python
        _render_action_buttons(item.path)
```

기존 `_render_action_placeholder` 함수는 제거하세요(더 이상 사용 안 함). 나머지는 모두 그대로 유지합니다.

---

### 4. `utils/styling.py` (인쇄용 CSS 추가)

기존 `_CSS`의 `</style>` 바로 앞에 다음을 **추가**하세요. 기존 CSS는 모두 그대로 유지.

```css

/* ============================================================
   인쇄용 CSS (Sprint 3)
   인쇄 시 UI 크롬을 모두 숨기고 리포트 이미지만 표시.
   ============================================================ */
@media print {
    .stApp, body, html {
        background: white !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* UI 크롬, 헤더, 액션 버튼 iframe 모두 숨김 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    header[data-testid="stHeader"],
    #MainMenu,
    .report-header,
    .report-section-title,
    .report-missing,
    .report-info-banner,
    .report-error-box,
    .back-to-main-link,
    iframe[title*="components"],
    iframe[title*="streamlit"] {
        display: none !important;
    }

    /* 이미지 박스 장식 제거 */
    .report-image-box {
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        background: white !important;
        page-break-inside: avoid;
    }
    .report-image-box img {
        max-width: 100% !important;
        height: auto !important;
        display: block;
        margin: 0 auto;
    }

    /* 메인 컨테이너 패딩 제거 */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
}
```

---

### 5. `BEHAVIOR.md` (Sprint 3 + MVP 완료 섹션 추가)

기존 BEHAVIOR.md 끝에 다음을 **추가**하세요(Sprint 0·1·2 섹션은 보존).

```markdown

---

## Sprint 3 — 액션 버튼 + 폴리싱 (Done) — MVP 완료

### 4개 액션 버튼 동작

각 리포트 이미지 아래에 4개 버튼이 가로 한 줄로 배치된다 (140px × 100px, 30px 간격).

#### 저장 (Save)
- 클릭 시 표시 중인 jpg 파일을 다운로드
- 다운로드 파일명은 원본 그대로 (예: 스팀월활동_01세_07월_02주.jpg)
- jpg는 iframe 내부에 base64 data URI로 인라인되어 별도 서버 요청 없음

#### 인쇄 (Print)
- 클릭 시 브라우저 인쇄 다이얼로그 표시
- `@media print` CSS로 사이드바, 헤더, 섹션 타이틀, 액션 버튼 iframe 모두 자동 숨김
- 인쇄 결과에는 리포트 이미지만 표시됨 (배경 흰색)

#### 메인 (Main)
- 클릭 시 현재 탭의 URL이 `/`로 변경되어 메인 화면으로 이동
- 새 탭에서 호출 시: 새 탭의 URL이 `/`로 변경됨 (메인 탭은 그대로)

#### 공유 (Share)
- 모바일/지원 브라우저: `navigator.share()`로 OS 공유 시트 표시
- 비지원 환경: `navigator.clipboard.writeText()`로 현재 URL을 클립보드에 복사하고 알림 표시
- 클립보드도 실패 시: prompt() 다이얼로그로 URL 표시 (사용자가 수동 복사)

### 버튼 외형
- 흰 배경 + 회색 테두리(#d0d0d0) + 둥근 모서리(14px)
- 호버 시 보라 테두리 + 살짝 위로 이동
- 아이콘 이미지 (assets/btn_save.png 등) 있으면 이미지 + 한글 라벨
- 아이콘 없으면 한글 라벨만 (크게 표시)

### iframe 격리
- 각 리포트 이미지마다 독립된 iframe(components.html, height=140)
- iframe 내부 JS는 `window.parent`로 부모 페이지 제어
- cross-origin 차단 시 fallback 로직 (window.top → window 자기 자신)

### 회귀 (Sprint 0·1·2 동작 모두 유지)
- 메인 페이지 단일 선택 동작 OK
- 기본값 (01세 / 05월 / 03주) OK
- 양쪽 미업로드 시 경고 다이얼로그 OK
- 새 탭 라우팅 OK
- 결과 페이지 lookup OK
- 파일 누락 시 노란 박스 OK
- 쿼리 오류 시 빨간 박스 + 메인 링크 OK

---

## MVP 완료 회고

### 완성된 파일 트리

```
project/
├── app.py
├── pages_local/{__init__,main_page,report_page}.py
├── utils/{__init__,mapping,filename,state,styling,url_builder,asset_helper,report_loader,action_buttons}.py
├── assets/                  (사용자 자산)
├── reports/                 (사용자 자산)
├── CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, BEHAVIOR.md
├── PROMPT_S0.md ~ PROMPT_S3.md
├── CLAUDE_CODE_KICKOFF_S0.md ~ CLAUDE_CODE_KICKOFF_S3.md
├── requirements.txt
└── README.md
```

### Do Not Break 11개 항목 최종 점검
1. 파일명 매핑 규칙 — 유지 ✓
2. Lookup 방식 — 유지 ✓ (업로드 사진은 합성/표시되지 않음)
3. 단일 선택 보장 — 유지 ✓ (radio/checkbox 미사용, button + type)
4. 기본값 — 유지 ✓
5. 새 탭 동작 — 유지 ✓ (HTML 앵커 + target="_blank")
6. 양쪽 미업로드 차단 — 유지 ✓
7. 파일 누락 대응 — 유지 ✓ (앱 죽지 않고 친화적 메시지)
8. Streamlit pages/ 자동인식 금지 — 유지 ✓ (pages_local/)
9. (해당 항목들 모두 유지)

### MVP 이후 후보 (Backlog)
SPRINT_PLAN.md의 "MVP 이후 후보" 섹션 참조.
```

---

### 6. 자체 검증

#### 6-1. 모듈 import

```bash
python -c "from utils.action_buttons import build_action_buttons_html; print('action_buttons OK')"
python -c "from pages_local.report_page import render; print('report_page OK')"
```

#### 6-2. `action_buttons` 구조 검증

다음을 임시 파일 `_verify_s3.py`로 작성·실행·삭제하세요.

```python
"""Sprint 3 자체 검증 — 임시 파일, 실행 후 삭제."""
from pathlib import Path
from utils.action_buttons import build_action_buttons_html

# 기존 reports/ 파일 활용
test_jpg = Path("reports/스팀월활동_01세_07월_02주.jpg")
assert test_jpg.exists(), f"테스트 파일 누락: {test_jpg}"

html = build_action_buttons_html(test_jpg)

# 구조 검증 항목
checks = [
    ("doSave()", "Save 핸들러"),
    ("doPrint()", "Print 핸들러"),
    ("doMain()", "Main 핸들러"),
    ("doShare()", "Share 핸들러"),
    ("window.parent.print()", "부모 페이지 print 호출"),
    ("window.parent.location.href", "부모 페이지 navigation"),
    ("navigator.share", "Web Share API"),
    ("navigator.clipboard.writeText", "Clipboard fallback"),
    ("data:image/jpeg;base64,", "이미지 base64 인코딩"),
    ("스팀월활동_01세_07월_02주.jpg", "다운로드 파일명 (한글)"),
    ('aria-label="저장"', "저장 버튼 aria-label"),
    ('aria-label="인쇄"', "인쇄 버튼 aria-label"),
    ('aria-label="메인"', "메인 버튼 aria-label"),
    ('aria-label="공유"', "공유 버튼 aria-label"),
]
for substr, desc in checks:
    assert substr in html, f"FAIL: {desc} 누락 ({substr!r} not in HTML)"
    print(f"PASS  {desc}")

# 미존재 파일 처리 — IMG_URI는 빈 문자열, doSave는 alert 분기
missing = Path("reports/__nonexistent_test__.jpg")
html_missing = build_action_buttons_html(missing)
assert 'const IMG_URI = "";' in html_missing, \
    "미존재 파일 처리 실패: IMG_URI가 빈 문자열이어야 함"
assert "저장할 이미지가 없습니다" in html_missing, \
    "미존재 파일 처리 실패: alert 메시지 누락"
print("PASS  미존재 jpg → IMG_URI 빈 문자열 + 안내 alert")

# 아이콘 fallback (assets/btn_save.png 등이 없을 때)
if not (Path("assets/btn_save.png").exists()):
    assert "action-btn-fallback" in html, \
        "아이콘 없을 때 텍스트 fallback 클래스 누락"
    print("PASS  아이콘 없을 때 텍스트 fallback (action-btn-fallback)")
else:
    assert "action-btn-label" in html, \
        "아이콘 있을 때 라벨 클래스 누락"
    print("PASS  아이콘 있을 때 라벨 동반 (action-btn-label)")

# CSS의 인쇄용 @media 규칙 검증
styling_path = Path("utils/styling.py")
styling_content = styling_path.read_text(encoding="utf-8")
print_checks = [
    ("@media print", "@media print 블록"),
    ("display: none !important", "UI 크롬 숨김"),
    ("page-break-inside: avoid", "이미지 페이지 분할 방지"),
]
for substr, desc in print_checks:
    assert substr in styling_content, f"FAIL: {desc} ({substr!r})"
    print(f"PASS  styling.py 인쇄용 CSS: {desc}")

print("\n모든 검증 통과")
```

실행:
```bash
python _verify_s3.py
# 결과 확인 후
del _verify_s3.py
```

#### 6-3. Streamlit 부팅 + 회귀

```bash
# 부팅
start /B streamlit run app.py --server.headless true --server.port 8501
# 5초 대기

# 메인 응답
powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:8501' -UseBasicParsing).StatusCode"
# 기대: 200

# 부팅 확인 후 프로세스 종료
```

#### 6-4. 회귀 — Sprint 0·1·2 자체 검증 재실행 (선택, 권장)

이전 Sprint의 핵심 검증을 한 번씩 다시 돌려서 회귀 없음을 확인:

```bash
# Sprint 0 — 매핑 카운트
python -c "from utils.mapping import AGE_LABELS, MONTH_LABELS, WEEK_LABELS; print(len(AGE_LABELS), len(MONTH_LABELS), len(WEEK_LABELS))"
# 기대: 2 12 4

# Sprint 0 — 파일명 빌드
python -c "from utils.filename import build_filename; print(build_filename('스팀월활동','01세','05월','03주'))"
# 기대: 스팀월활동_01세_05월_03주.jpg

# Sprint 1 — URL 빌더
python -c "from utils.url_builder import build_report_url; print(build_report_url('01세','05월','03주',True,True))"
# 기대: ?page=report&age=01%EC%84%B8&month=05%EC%9B%94&week=03%EC%A3%BC&steam=1&art=1

# Sprint 2 — report_loader 정상 케이스
python -c "
from utils.report_loader import load_from_query_params, ReportContext
class FakeQP(dict):
    def get(self, k, default=''): return super().get(k, default)
r = load_from_query_params(FakeQP({'age':'01세','month':'07월','week':'02주','steam':'1','art':'1'}))
assert isinstance(r, ReportContext) and len(r.items) == 2
print('S2 회귀 OK')
"
```

---

### 7. Do Not

- 액션 버튼을 `st.button`이나 `st.download_button`으로 구현 금지 (ADR-004에 따라 HTML/JS 커스텀 블록만)
- 메인 페이지(`main_page.py`) 절대 수정 금지
- 매핑/파일명/URL빌더/asset 헬퍼/state/report_loader 수정 금지
- jpg를 외부 URL이나 서버 엔드포인트로 노출 금지 → data URI 내장만 사용
- 사용자가 업로드한 사진을 액션 버튼 처리에 끌어들이지 말 것 (Lookup만! ADR-001)
- 인쇄용 `@media print` 규칙은 기존 화면 CSS를 깨지 않도록 `@media print` 블록 내부에만 작성
- 한글 파일명을 영문으로 변환하지 말 것 (다운로드 파일명도 한글 그대로)
- `_render_action_placeholder` 함수와 그 안의 placeholder div HTML은 더 이상 호출되지 않으므로 제거. 단, CSS의 `.action-buttons-area`, `.action-btn-placeholder` 클래스는 무해하므로 그대로 둠.

---

### 8. 보고 형식

```
## Sprint 3 완료 보고 — MVP 완성

### 수정/생성된 파일
- [파일 경로 + 한 줄 설명] × N

### 자체 검증 결과
- [ ] 모듈 import: action_buttons / report_page
- [ ] _verify_s3.py 구조 검증 (모든 checks PASS)
- [ ] _verify_s3.py 파일 삭제
- [ ] Streamlit HTTP 200
- [ ] Sprint 0·1·2 회귀 검증 통과

### 검증 항목별 상세
- doSave/doPrint/doMain/doShare 핸들러: PASS
- window.parent navigation/print: PASS
- navigator.share + clipboard fallback: PASS
- 한글 다운로드 파일명: PASS
- 미존재 jpg 처리 (IMG_URI 빈 문자열 + alert): PASS
- 아이콘 fallback: PASS
- styling.py @media print 블록: PASS

### 알려진 한계
- 액션 버튼 아이콘(assets/btn_save.png 등) 미배치 시 텍스트 라벨로 표시
  → 사용자가 4개 아이콘을 배치하면 자동으로 이미지 표시 전환됨
- jpg 파일이 크면 base64 인코딩으로 HTML 페이로드 증가 (200KB jpg → ~270KB iframe)
  → MVP 범위에서는 허용. 향후 정적 서빙 도입 시 개선 가능
- 인쇄 시 jpg 한 장이 한 페이지를 넘는 경우 페이지 분할 처리는 브라우저 기본 동작에 위임

### 사용자 수동 확인 요청 항목 (전체 통합 시나리오)
1. 메인 화면 정상 진입 + 기본값 표시
2. 만1세 / 7월 여름을 만나요 / 2주차 선택 + 양쪽에 임의 사진 업로드 + 생성 클릭
3. 새 탭에서 결과 페이지 열림 + 두 jpg 모두 표시 + 각 8개 버튼(2세트) 표시
4. 저장 클릭 → 다운로드 폴더에 "스팀월활동_01세_07월_02주.jpg" 저장 확인
5. 인쇄 클릭 → 브라우저 인쇄 미리보기에 리포트 이미지만 표시되는지 (UI 크롬 숨김 확인)
6. 공유 클릭 → 데스크톱 Chrome/Edge에서 "URL이 클립보드에 복사되었습니다" 알림 표시
7. 메인 클릭 → 새 탭이 메인 화면으로 이동
8. assets/에 btn_save.png 등 4개 아이콘 배치 후 새로고침 → 텍스트 라벨이 이미지로 전환되는지

### MVP 완성
- CLAUDE.md "Do Not Break" 11개 항목 모두 통과
- BEHAVIOR.md에 Sprint 0~3 + MVP 완료 회고 섹션 완성
- 다음 작업은 SPRINT_PLAN.md "MVP 이후 후보" 항목 중 선택하여 새 Sprint 패키지 요청
```
