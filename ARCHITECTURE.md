# ARCHITECTURE.md

> 토들러 아트 프로그램 활동 레포트 메이커의 아키텍처 결정 기록(ADR).

---

## 1. 시스템 다이어그램 (논리)

```
┌──────────────────────────────────────────────────────────────┐
│                      Streamlit App (단일 진입점)              │
│                          app.py                              │
│                             │                                 │
│        ┌────────────────────┴────────────────────┐            │
│        │  query_params["page"] 분기              │            │
│        └────────────────────┬────────────────────┘            │
│              ┌──────────────┴──────────────┐                 │
│              ▼                              ▼                │
│   ┌──────────────────────┐      ┌──────────────────────┐    │
│   │  main_page.py        │      │  report_page.py      │    │
│   │  - 3개 단일선택 그룹  │      │  - lookup            │    │
│   │  - 2개 업로드 박스    │      │  - 이미지 표시         │    │
│   │  - 생성 버튼          │      │  - 4 액션 버튼        │    │
│   └──────────┬───────────┘      └──────────┬───────────┘    │
│              │                              │                │
│              ▼                              ▼                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  utils/ (mapping, filename, state, styling)         │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
   ┌──────────┐                  ┌──────────┐
   │ assets/  │                  │ reports/ │
   │ (UI img) │                  │ (jpg DB) │
   └──────────┘                  └──────────┘
```

---

## 2. 데이터 흐름

### 2.1 메인 → 결과 (생성 클릭)

```
[user] → 연령/월/주차 선택 + 사진 업로드
   ↓
[session_state] 저장
   ↓
[user] "생성" 버튼 클릭
   ↓
[validate] 양쪽 모두 미업로드면 경고 팝업, 중단
   ↓
[build URL] /?page=report&age=01세&month=05월&week=03주&steam=1&art=1
   ↓
[new tab] target="_blank" 앵커 클릭
   ↓
[report_page] query_params 읽기 → lookup → 표시
```

### 2.2 결과 페이지 lookup

```
query_params = { page, age, month, week, steam?, art? }
   ↓
candidates = []
if steam: candidates.append(f"스팀월활동_{age}_{month}_{week}.jpg")
if art:   candidates.append(f"아트활동_{age}_{month}_{week}.jpg")
   ↓
for each candidate:
    path = reports / candidate
    if path.exists(): 표시
    else: "준비되지 않았습니다" 안내
```

---

## 3. 핵심 아키텍처 결정 (ADR)

### ADR-001: Lookup 방식 채택

**상황**: 활동 레포트는 미리 정해진 콘텐츠(연령/월/주차별)로, 사용자가 올린 사진이 결과 이미지에 합성되지 않는다.

**결정**: 동적 합성이 아닌 **사전 제작 jpg 조회** 방식을 사용한다.

**이유**:
- 디자인 품질 보장 (전문가가 미리 만든 결과물)
- 백엔드 부담 없음 (이미지 합성/AI 호출 불필요)
- 단순한 파일명 규칙으로 매핑 가능

**대안 검토**: 업로드 사진 합성 방식. 디자인 품질 관리가 어렵고 합성 결과 예측 불가. 기각.

---

### ADR-002: 새 탭 라우팅 = 쿼리 파라미터 기반 단일 앱

**상황**: 명세상 결과 화면이 "별도의 창"으로 표시되어야 함.

**결정**: Streamlit의 multi-page(`pages/`) 자동 인식 기능을 쓰지 않고, **단일 진입점(`app.py`) + `?page=...` 쿼리 파라미터 + HTML `target="_blank"` 앵커**로 새 탭 라우팅을 구현한다.

**이유**:
- Streamlit `pages/` 폴더는 사이드바 네비게이션을 강제로 만든다. 메인 화면 디자인이 깨진다.
- 쿼리 파라미터는 새 탭 간 데이터 전달에 자연스럽다.
- Lookup에 필요한 정보(age/month/week/카테고리 플래그)는 모두 텍스트라 URL 전달이 가능하다.

**트레이드오프**: 업로드된 실제 파일은 새 탭에 전달되지 않는다. 하지만 lookup 방식이라 파일 내용이 필요하지 않으므로 문제없음.

---

### ADR-003: 단일선택 = 커스텀 버튼 + session_state

**상황**: 명세는 "체크박스"라고 표현하지만 동작은 단일 선택이며, 디자인은 카드형 버튼이다.

**결정**: `st.radio`나 `st.checkbox`를 쓰지 않고, **`st.button` 격자 + session_state로 선택 상태 추적 + CSS로 선택/비선택 외형 차별화**한다.

**이유**:
- `st.radio`는 디자인 커스터마이징이 매우 제한적이다 (목업의 카드 버튼 외형 구현 불가).
- `st.button` + session_state는 외형 자유도가 높고 단일 선택 로직도 명시적이다.

**구현 패턴**:
```python
cols = st.columns(2)
for i, label in enumerate(["만1세", "만2세"]):
    code = AGE_MAP[label]
    is_selected = (st.session_state[AGE_KEY] == code)
    btn_class = "btn-selected" if is_selected else "btn-unselected"
    with cols[i]:
        if st.button(label, key=f"age_{code}", use_container_width=True):
            st.session_state[AGE_KEY] = code
            st.rerun()
```

CSS로 `[data-testid="stButton"]` 내부 버튼을 클래스 기반으로 스타일링.

---

### ADR-004: 액션 버튼은 HTML/JS 커스텀 블록

**상황**: 결과 페이지의 저장/인쇄/메인/공유 버튼은 명세에 따르면 4개 모두 이미지 버튼이어야 한다.

**결정**: `st.components.v1.html`로 **HTML+CSS+JS 단일 블록**을 만든다. Streamlit 기본 위젯과 섞지 않는다.

**이유 및 구현**:
| 버튼 | 동작 | 구현 |
|---|---|---|
| 저장 | jpg 다운로드 | `<a download>` 또는 fetch + blob |
| 인쇄 | 브라우저 인쇄 | `window.print()` |
| 메인 | 메인 화면으로 | `window.location.href = '/'` |
| 공유 | 공유 시트 / URL 복사 | `navigator.share()` + clipboard fallback |

`st.download_button`은 텍스트 버튼만 가능하므로 사용하지 않는다.

---

### ADR-005: 이미지 사이즈를 CSS 변수로 변수화

**상황**: 명세에 "추후 크기변화나 위치변화를 주어 조정할 수 있도록 합니다"라는 요구가 있다.

**결정**: 모든 사이즈 값은 `utils/styling.py`의 단일 CSS 블록 내 `:root` 변수로 선언한다.

**이유**: 향후 사이즈 조정이 한 곳에서만 발생하도록 보장. 매직 넘버 분산 방지.

---

### ADR-006: 매핑 dict는 utils/mapping.py의 단일 소스

**상황**: 라벨↔코드 변환이 여러 곳에서 필요 (메인 페이지 UI, URL 빌드, 파일명 생성).

**결정**: 모든 매핑 dict는 `utils/mapping.py`에 상수로 선언하고, **양방향 lookup 헬퍼 함수**를 제공한다.

**제공 함수**:
- `age_label_to_code(label) -> code`
- `age_code_to_label(code) -> label`
- `month_label_to_code(label) -> code`
- `week_to_code(week_int) -> code`
- `AGE_LABELS`, `MONTH_LABELS`, `WEEK_LABELS` (UI 렌더링용 순서 보존 리스트)

---

### ADR-007: pages_local/ 네이밍

**상황**: Streamlit은 진입점과 같은 디렉토리의 `pages/` 폴더 안 `.py` 파일을 자동으로 페이지로 인식한다.

**결정**: 우리의 페이지 모듈 폴더는 `pages_local/`이라고 이름 짓는다.

**이유**: `pages/`라고 이름 지으면 Streamlit이 사이드바에 자동 네비게이션을 만들어 디자인을 망친다.

---

## 4. 컴포넌트 책임 분리

| 모듈 | 책임 | 의존 |
|---|---|---|
| `app.py` | 진입점, `set_page_config`, 라우터 | streamlit, pages_local |
| `pages_local/main_page.py` | 메인 UI 렌더링, 입력 검증, 새 탭 링크 생성 | utils.* |
| `pages_local/report_page.py` | query_params 파싱, lookup, 결과 렌더링 | utils.* |
| `utils/mapping.py` | 라벨↔코드 양방향 매핑 | (없음) |
| `utils/filename.py` | 파일명 빌드 + 존재 확인 | utils.mapping |
| `utils/state.py` | session_state 키 상수, 초기화 함수 | streamlit |
| `utils/styling.py` | CSS 인젝션 (디자인 토큰 + 컴포넌트 스타일) | streamlit |

**규칙**: `pages_local/*`는 `utils/*`만 import한다. `utils/*` 사이에서는 단방향 의존(mapping → filename)만 허용.

---

## 5. 비기능 요구사항

| 항목 | 목표 |
|---|---|
| 첫 로딩 | 3초 이내 (`assets/` 이미지 크기 합 5MB 이내 권장) |
| 새 탭 결과 표시 | 1초 이내 (단순 파일 조회) |
| 동시 사용자 | 단일 사용자 우선 (교사 1명 사용 시나리오) |
| 브라우저 호환 | Chrome, Edge 최신 (Web Share API 지원 환경) |
| 한글 파일명 처리 | UTF-8 일관 유지 (Windows/Linux 모두) |

---

## 6. 향후 확장 시 고려할 부분

| 확장 | 영향 |
|---|---|
| 연령 추가 (만3세 등) | `AGE_MAP` 추가 + `/reports/`에 신규 jpg 배치 + UI 컬럼 수 조정 |
| 월별 주제 변경 | `MONTH_MAP` 라벨만 수정 (코드 `0N월`는 유지) |
| 동적 합성 도입 | ADR-001 재검토 필요. lookup 폴더 옆에 합성 파이프라인 추가 |
| 다국어 지원 | 라벨은 다국어, 코드(파일명)는 단일 체계 유지 |
| 사용자별 저장소 | session_state → DB 또는 파일 시스템 도입 시 멀티유저 고려 |

---

## 7. 위험 요소

| 위험 | 대응 |
|---|---|
| `/reports/` 파일 누락 | 파일 존재 확인 후 친화적 메시지 표시 (앱 죽지 않게) |
| 새 탭 차단 (팝업 차단기) | HTML 앵커 사용 (JS `window.open`이 아닌 사용자 클릭 기반) |
| Streamlit 버전 차이 | `st.query_params`는 1.30+ 기준. requirements 명시 |
| 한글 URL 인코딩 | 파라미터에 한글 코드(`01세`)가 들어가므로 `urllib.parse.quote` 명시 사용 |
| 모바일 Share API 미지원 | `navigator.share` 미지원 시 clipboard 복사 fallback |
