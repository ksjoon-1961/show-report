# PROMPT_S2.md — Sprint 2: 결과 페이지 lookup + 표시

> Sprint 0·1 산출물이 모두 존재해야 합니다.

---

## 작업 지시 (Claude Code에게 그대로 전달)

당신은 토들러 아트 프로그램 활동 레포트 메이커 프로젝트의 Sprint 2를 수행합니다.

### 0. 사전 읽기 (필수)

1. `CLAUDE.md` — 섹션 4 핵심 원칙(특히 Lookup 방식), 섹션 6 라우팅 스펙, 섹션 9 Do Not Break(#7 파일 누락 대응)
2. `ARCHITECTURE.md` — **ADR-001 Lookup 방식**, **ADR-002 새 탭 라우팅** 재확인. 데이터 흐름 섹션 2.2 lookup 알고리즘 그대로 따름
3. `SPRINT_PLAN.md` — Sprint 2 산출물 + 인수 조건
4. 기존 코드 — `pages_local/report_page.py` (현재 placeholder), `utils/filename.py`, `utils/mapping.py`, `utils/styling.py`

읽기 후 한 줄 출력: "Sprint 2 시작: 결과 페이지 lookup + 표시"

---

### 1. 작업 범위

**수정할 파일**:
- `pages_local/report_page.py` — placeholder → 실제 lookup 및 표시로 전면 재작성
- `utils/styling.py` — 결과 페이지용 CSS 추가 (기존 CSS 유지하고 추가만)
- `BEHAVIOR.md` — Sprint 2 섹션 추가

**새로 생성할 파일**:
- `utils/report_loader.py` — query_params 파싱 + lookup 로직 캡슐화

**절대 수정 금지**:
- `app.py`
- `pages_local/main_page.py`
- `utils/mapping.py`
- `utils/filename.py`
- `utils/state.py`
- `utils/url_builder.py`
- `utils/asset_helper.py`
- `requirements.txt`
- 모든 .md 문서 (CLAUDE/ARCHITECTURE/SPRINT_PLAN/PROMPT_S0~S2)

---

### 2. `utils/report_loader.py` (신규)

```python
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
```

---

### 3. `pages_local/report_page.py` (전면 재작성)

기존 파일을 다음으로 **완전히 교체**하세요.

```python
"""결과 페이지 — query_params 기반 lookup + 표시.

session_state에 의존하지 않는다. 새 탭이라 메인 페이지 state는 공유되지 않음.
모든 정보는 st.query_params에서 읽고 utils.report_loader가 검증/조립.
"""
import streamlit as st

from utils.report_loader import (
    load_from_query_params,
    ReportContext, QueryError, ReportItem,
)


# ============================================================
# 헬퍼
# ============================================================

def _render_query_error(err: QueryError) -> None:
    """잘못된 쿼리 파라미터일 때 오류 + 메인 링크."""
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


def _render_report_header(ctx: ReportContext) -> None:
    st.markdown(
        f'<div class="report-header">'
        f'<h1>토들러 아트 활동 레포트</h1>'
        f'<p class="report-meta">'
        f'{ctx.age_label}  ·  {ctx.month_label}  ·  {ctx.week_label}'
        f'</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_action_placeholder() -> None:
    """4개 액션 버튼 placeholder. Sprint 3에서 실제 동작 구현."""
    st.markdown(
        '<div class="action-buttons-area">'
        '<div class="action-btn-placeholder">💾<br>저장</div>'
        '<div class="action-btn-placeholder">🖨️<br>인쇄</div>'
        '<div class="action-btn-placeholder">🏠<br>메인</div>'
        '<div class="action-btn-placeholder">🔗<br>공유</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_report_item(item: ReportItem) -> None:
    """단일 리포트 항목 (이미지 또는 누락 메시지) + 액션 버튼."""
    st.markdown(
        f'<div class="report-section-title">{item.type_label}</div>',
        unsafe_allow_html=True,
    )

    if item.exists:
        st.markdown('<div class="report-image-box">', unsafe_allow_html=True)
        st.image(str(item.path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        _render_action_placeholder()
    else:
        st.markdown(
            f'<div class="report-missing">'
            f'<div class="report-missing-icon">📭</div>'
            f'<div class="report-missing-title">해당 레포트가 준비되지 않았습니다</div>'
            f'<div class="report-missing-detail">{item.path.name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# 진입점
# ============================================================

def render() -> None:
    result = load_from_query_params(st.query_params)

    if isinstance(result, QueryError):
        _render_query_error(result)
        return

    _render_report_header(result)

    for item in result.items:
        _render_report_item(item)

    # 모든 항목이 미존재인 경우 추가 안내
    if not result.has_any_existing:
        st.markdown(
            '<div class="report-info-banner">'
            '💡 선택하신 조건의 레포트가 아직 준비되지 않았습니다. '
            '<a href="/" target="_self">메인 화면으로 돌아가기</a>'
            '</div>',
            unsafe_allow_html=True,
        )
```

---

### 4. `utils/styling.py` (CSS 추가)

기존 `_CSS` 변수의 `</style>` 바로 앞에 다음 블록을 **추가**합니다. 기존 CSS는 그대로 유지하세요.

```css

/* ============================================================
   결과 페이지 (Sprint 2)
   ============================================================ */

/* 결과 페이지 헤더 */
.report-header {
  text-align: center;
  margin: 30px auto;
  padding-bottom: 25px;
  border-bottom: 3px solid var(--primary-color);
  max-width: 1800px;
}
.report-header h1 {
  margin: 0;
  color: #333;
  font-size: 38px;
}
.report-meta {
  color: var(--primary-color);
  font-size: 22px;
  font-weight: 700;
  margin: 15px 0 0;
}

/* 섹션 타이틀 (STEAM WALL 활동 / 아트 활동) */
.report-section-title {
  font-size: 26px;
  font-weight: 700;
  margin: 35px 0 18px;
  padding: 8px 16px;
  border-left: 8px solid var(--primary-color);
  color: #333;
}

/* 이미지 박스 */
.report-image-box {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin: 0 auto 24px;
  max-width: 1600px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.report-image-box img {
  border-radius: 8px;
  display: block;
}

/* 파일 누락 박스 */
.report-missing {
  background: #fff8e1;
  border: 2px solid #ffc107;
  border-radius: 16px;
  padding: 50px 30px;
  text-align: center;
  margin: 0 auto 30px;
  max-width: 1600px;
}
.report-missing-icon { font-size: 56px; margin-bottom: 16px; }
.report-missing-title {
  font-size: 22px; font-weight: 700; color: #856404; margin-bottom: 12px;
}
.report-missing-detail {
  font-size: 16px; color: #6c757d;
  font-family: 'Consolas', 'Courier New', monospace;
}

/* 액션 버튼 placeholder (Sprint 2 단계) */
.action-buttons-area {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 24px auto 50px;
  max-width: 1600px;
}
.action-btn-placeholder {
  width: 140px;
  height: 100px;
  background: #f0f0f0;
  border: 2px dashed #b0b0b0;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #666;
  text-align: center;
  line-height: 1.4;
}

/* 쿼리 오류 박스 */
.report-error-box {
  background: #ffebee;
  border: 2px solid #ef5350;
  border-radius: 16px;
  padding: 40px;
  margin: 60px auto;
  max-width: 800px;
  text-align: center;
}
.report-error-box h3 { color: #c62828; margin-top: 0; font-size: 26px; }
.report-error-box p {
  color: #555; font-size: 16px;
  font-family: 'Consolas', 'Courier New', monospace;
}

/* 메인으로 가기 링크 */
.back-to-main-link {
  display: inline-block;
  margin: 20px auto;
  padding: 14px 28px;
  background: var(--primary-color);
  color: white !important;
  text-decoration: none !important;
  border-radius: 10px;
  font-weight: 700;
  font-size: 16px;
}
.back-to-main-link:hover { opacity: 0.9; transform: translateY(-1px); }

/* 모든 미존재 시 정보 배너 */
.report-info-banner {
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  font-size: 18px;
  color: #1565c0;
  max-width: 1200px;
  margin: 30px auto;
}
.report-info-banner a { color: var(--primary-color); font-weight: 700; }
```

추가 위치 가이드: 기존 `</style>` 바로 위에 붙여 넣으세요. 다른 부분은 손대지 않습니다.

---

### 5. `BEHAVIOR.md` (Sprint 2 섹션 추가)

기존 BEHAVIOR.md 끝에 다음 섹션을 **추가**하세요(기존 Sprint 0·1 섹션 유지).

```markdown

---

## Sprint 2 — 결과 페이지 lookup + 표시 (Done)

### 정상 lookup 동작
- URL `/?page=report&age=01세&month=07월&week=02주&steam=1&art=1` 직접 접근 시:
  - 헤더에 "토들러 아트 활동 레포트" + "만1세 · 7월 여름을 만나요 · 2주차" 표시
  - "STEAM WALL 활동" 섹션에 `스팀월활동_01세_07월_02주.jpg` 표시
  - "아트 활동" 섹션에 `아트활동_01세_07월_02주.jpg` 표시
  - 각 이미지 아래 4개 액션 버튼 placeholder 표시
- STEAM WALL만 업로드 (steam=1, art 없음): 스팀월활동 jpg 1개만 표시
- Art만 업로드 (art=1, steam 없음): 아트활동 jpg 1개만 표시
- STEAM이 먼저, Art가 다음 순서로 표시됨

### 파일 누락 처리
- 선택 조합의 jpg가 `/reports/`에 없으면 노란색 박스에 "해당 레포트가 준비되지 않았습니다" + 파일명 표시
- 앱 죽지 않음, 다른 항목은 정상 처리됨

### 모든 항목 미존재
- 두 카테고리 모두 표시하지만 둘 다 파일 없음일 때 추가로 파란 배너 표시 + 메인 링크

### 쿼리 파라미터 오류
- age/month/week 코드가 매핑에 없거나 누락된 경우 빨간 박스로 오류 메시지 표시
- 모든 오류 사유가 누적되어 한 번에 표시됨
- 하단에 "메인 화면으로 돌아가기" 링크
- steam=1, art=1 둘 다 없으면 오류로 처리

### 시각 일관성
- 결과 페이지에도 사이드바 / Streamlit 기본 메뉴 / 헤더 모두 숨김
- 배경색 #f2f2f2 유지
- 이미지 박스는 흰 배경 + 둥근 모서리 + 그림자
```

---

### 6. 자체 검증

#### 6-1. 모듈 import

```bash
python -c "from utils.report_loader import load_from_query_params, ReportContext, QueryError, ReportItem; print('report_loader OK')"
python -c "from pages_local.report_page import render; print('report_page OK')"
```

#### 6-2. `report_loader` 케이스 테스트

다음 스크립트를 임시 파일로 만들어 실행하고 결과를 보고에 포함하세요. **임시 파일은 검증 후 삭제**.

`_verify_s2.py`:
```python
"""Sprint 2 자체 검증 — 임시 파일, 실행 후 삭제."""
from utils.report_loader import (
    load_from_query_params, ReportContext, QueryError,
)


class FakeQP(dict):
    """st.query_params 흉내."""
    def get(self, k, default=""):
        return super().get(k, default)


def case(name, qp_dict, expect_type, extra_check=None):
    result = load_from_query_params(FakeQP(qp_dict))
    assert isinstance(result, expect_type), \
        f"[{name}] expected {expect_type.__name__}, got {type(result).__name__}"
    if extra_check:
        extra_check(result)
    print(f"PASS  {name}")


# 케이스 1: 정상, 양쪽 업로드, 기존 reports/ 파일과 매칭
case("C1 양쪽 업로드 + 파일 존재",
     {"age": "01세", "month": "07월", "week": "02주",
      "steam": "1", "art": "1"},
     ReportContext,
     lambda r: (
         (len(r.items) == 2) and
         (r.items[0].type_code == "스팀월활동") and
         (r.items[1].type_code == "아트활동") and
         all(item.exists for item in r.items)  # 기존 파일 두 개 모두 존재해야 함
     ) or (_ for _ in ()).throw(AssertionError(f"items={r.items}")))

# 케이스 2: STEAM만, 파일 존재
case("C2 STEAM만 업로드",
     {"age": "01세", "month": "07월", "week": "02주", "steam": "1"},
     ReportContext,
     lambda r: (
         len(r.items) == 1 and r.items[0].type_code == "스팀월활동"
         and r.items[0].exists
     ) or (_ for _ in ()).throw(AssertionError(f"items={r.items}")))

# 케이스 3: Art만, 파일 존재
case("C3 Art만 업로드",
     {"age": "01세", "month": "07월", "week": "02주", "art": "1"},
     ReportContext,
     lambda r: (
         len(r.items) == 1 and r.items[0].type_code == "아트활동"
         and r.items[0].exists
     ) or (_ for _ in ()).throw(AssertionError(f"items={r.items}")))

# 케이스 4: 정상이지만 파일 미존재 (다른 조합)
case("C4 정상 쿼리 + 파일 미존재",
     {"age": "02세", "month": "12월", "week": "04주",
      "steam": "1", "art": "1"},
     ReportContext,
     lambda r: (
         not r.has_any_existing
     ) or (_ for _ in ()).throw(AssertionError(f"has_any={r.has_any_existing}")))

# 케이스 5: 잘못된 age 코드
case("C5 잘못된 age",
     {"age": "99세", "month": "05월", "week": "03주", "steam": "1"},
     QueryError)

# 케이스 6: 잘못된 month 코드
case("C6 잘못된 month",
     {"age": "01세", "month": "13월", "week": "03주", "steam": "1"},
     QueryError)

# 케이스 7: 잘못된 week 코드
case("C7 잘못된 week",
     {"age": "01세", "month": "05월", "week": "99주", "steam": "1"},
     QueryError)

# 케이스 8: 카테고리 플래그 없음
case("C8 플래그 없음",
     {"age": "01세", "month": "05월", "week": "03주"},
     QueryError)

# 케이스 9: 다중 오류 누적 (age 잘못 + 플래그 없음)
def check_multi(r):
    if "/" not in r.message:
        raise AssertionError(f"expected multi-error, got: {r.message}")

case("C9 다중 오류 누적",
     {"age": "99세", "month": "99월", "week": "99주"},
     QueryError, check_multi)

print("\n모든 케이스 통과 (C1~C9)")
```

실행:
```bash
python _verify_s2.py
# 출력 확인 후
del _verify_s2.py
```

#### 6-3. Streamlit 부팅 + 결과 페이지 응답

```bash
# 부팅
start /B streamlit run app.py --server.headless true --server.port 8501

# 5초 대기

# 결과 페이지 직접 요청 — PowerShell의 경우 Invoke-WebRequest 사용 권장
# (curl은 Windows에서 % 이스케이프 문제 발생 가능)
powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:8501/?page=report&age=01%E1%84%89%E1%85%A6&month=07%E1%84%8B%E1%85%AF%E1%86%AF&week=02%E1%84%8C%E1%85%AE&steam=1&art=1' -UseBasicParsing).StatusCode"
# 기대: 200

# 또는 단순 메인 응답으로 부팅만 확인:
powershell -Command "(Invoke-WebRequest -Uri 'http://localhost:8501' -UseBasicParsing).StatusCode"
# 기대: 200
```

부팅 확인 후 프로세스 종료. URL 인코딩이 까다로우면 메인 응답만 확인해도 무방하고, 결과 페이지의 시각 검증은 사용자 수동 단계에 맡깁니다.

---

### 7. Do Not

- 메인 페이지(`main_page.py`)는 절대 수정하지 말 것
- 매핑/파일명/URL빌더/asset 헬퍼/state는 수정 금지 (Sprint 1까지 확정됨)
- 액션 버튼(저장/인쇄/메인/공유)의 **실제 동작** 구현 금지 → placeholder div만 (Sprint 3 범위)
- 업로드된 사진 자체를 표시하려는 시도 금지 (Lookup만! ADR-001)
- `/reports/` 폴더 내용물 임의 삭제/이동 금지
- `st.error`, `st.warning` 같은 Streamlit 기본 박스로 어쩔 수 없이 표시할 때는 한 곳에만 쓰고, 가능하면 커스텀 HTML 블록을 우선 사용 (디자인 일관성)
- 한글 URL 디코딩을 별도로 시도 금지 — Streamlit이 자동 디코딩한 `st.query_params`를 그대로 사용

---

### 8. 보고 형식

```
## Sprint 2 완료 보고

### 수정/생성된 파일
- [파일 경로 + 한 줄 설명] × N

### 자체 검증 결과
- [ ] 모듈 import: report_loader / report_page
- [ ] 케이스 C1~C9 (총 9개)
- [ ] Streamlit HTTP 200 (메인 또는 결과 페이지)
- [ ] 임시 검증 파일 _verify_s2.py 삭제

### 케이스별 상세
- C1 양쪽 업로드 + 파일 존재: PASS
- C2 STEAM만: PASS
- ...
- C9 다중 오류 누적: PASS

### 알려진 한계
- 액션 버튼 4개는 placeholder div 상태 (Sprint 3에서 실제 동작 구현)
- 다른 연령/월/주차 조합은 reports/에 파일이 없어 "준비되지 않았습니다" 메시지가 표시됨
  → 사용자가 jpg를 추가하면 자동으로 이미지로 전환됨

### 사용자 수동 확인 요청 항목
1. 메인 화면에서 만1세 / 7월 여름을 만나요 / 2주차 선택 후, 양쪽 영역에 임의 사진 업로드 → 생성 클릭
2. 새 탭에서 결과 페이지가 열리고 스팀월활동 + 아트활동 2장이 모두 표시되는지
3. 만2세 / 12월 / 4주차 등 파일 없는 조합으로 시도 시 "준비되지 않았습니다" 박스가 표시되는지
4. URL을 임의로 수정해서(/?page=report&age=99세&...) 접근 시 빨간 오류 박스 + 메인 링크가 표시되는지
5. 사이드바 없이 결과가 단독으로 보이는지

### 다음 단계
Sprint 3 — 액션 버튼(저장/인쇄/메인/공유) + 폴리싱 준비 완료. PROMPT_S3.md를 사용자에게 요청.
```
