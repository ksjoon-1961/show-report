# 토들러 아트 프로그램 활동 레포트 메이커

> Claude Code 세션의 영속적 컨텍스트 파일. 모든 세션 시작 시 이 문서를 먼저 읽고 작업한다.

---

## 1. 프로젝트 개요

**이름**: STEAM WALL 토들러 아트 프로그램 활동 레포트 메이커

**목적**: 어린이집/유치원 교사가 연령·생활주제·주차를 선택하고 활동 사진을 업로드하면, 미리 만들어진 활동 레포트 이미지를 조회하여 결과 페이지에 표시·다운로드·인쇄·공유하는 Streamlit 기반 웹 애플리케이션.

**핵심 모델**: **Lookup 방식** — 업로드된 사진 자체는 합성에 쓰이지 않는다. 사용자 선택값 + 업로드 카테고리(STEAM WALL / Art) 플래그를 키로 사용해 `/reports/` 폴더에서 미리 만들어진 jpg를 조회한다.

---

## 2. 기술 스택

| 항목 | 선택 | 비고 |
|---|---|---|
| 언어 | Python 3.10+ | |
| UI 프레임워크 | Streamlit | `>=1.30` (st.query_params 사용) |
| 이미지 처리 | Pillow | 최소 사용 (lookup 방식) |
| 커스텀 위젯 | HTML/CSS/JS 인젝션 | 액션 버튼, 단일선택 버튼 스타일 |
| 운영체제 | Windows (개발), Linux (배포 대비) | 경로는 `pathlib` 사용 |

---

## 3. 폴더 구조

```
project/
├── app.py                      # 진입점 + 페이지 라우터
├── pages_local/                # ⚠ Streamlit 자동인식 'pages/' 폴더가 아님
│   ├── __init__.py
│   ├── main_page.py            # 메인 선택 화면 렌더러
│   └── report_page.py          # 결과 표시 화면 렌더러
├── utils/
│   ├── __init__.py
│   ├── mapping.py              # 라벨 ↔ 파일명 코드 변환
│   ├── filename.py             # 리포트 파일명 생성 + 존재 확인
│   ├── state.py                # session_state 초기화/접근 헬퍼
│   └── styling.py              # CSS 인젝션
├── assets/                     # UI 이미지 (커밋 대상)
│   ├── header.png
│   ├── age_icon.png
│   ├── topic_icon.png
│   ├── week_icon.png
│   ├── camera_icon.png
│   ├── btn_save.png
│   ├── btn_print.png
│   ├── btn_main.png
│   └── btn_share.png
├── reports/                    # 미리 만들어진 리포트 jpg (커밋 대상)
│   ├── 스팀월활동_01세_05월_03주.jpg
│   ├── 아트활동_01세_05월_03주.jpg
│   └── ...
├── CLAUDE.md                   # 이 문서
├── BEHAVIOR.md                 # 회귀 테스트용 동작 명세
├── ARCHITECTURE.md             # 아키텍처 결정 기록
├── requirements.txt
└── README.md
```

**주의**: Streamlit이 자동 인식하는 `pages/` 폴더를 쓰면 사이드바에 자동 네비게이션이 생긴다. 우리는 단일 진입점 + 쿼리 파라미터 라우팅을 사용하므로 폴더 이름은 `pages_local/`로 한다.

---

## 4. 핵심 동작 원칙

1. **Lookup만 한다**: 사용자가 올린 사진은 절대 합성하지 않는다. 단지 "이 카테고리 jpg를 보여줄지 말지"의 플래그일 뿐이다.
2. **새 탭 라우팅**: 결과 화면은 같은 Streamlit 앱의 다른 페이지가 아니라 **새 탭으로 열린 같은 앱 + `?page=report&...` 쿼리 파라미터**다.
3. **단일 선택**: 연령/월/주차는 모두 단일 선택이다. 외형은 체크박스/카드 버튼이지만 동작은 라디오다.
4. **기본값**: 첫 진입 시 만1세 / 3월 어린이집이 좋아요 / 1주차가 미리 선택되어 있다.
5. **양쪽 미업로드 시 차단**: 두 사진 모두 없으면 생성 버튼을 눌렀을 때 경고 팝업 후 동작 중단.
6. **고정 비율 + 비례 조정 가능**: 기준 캔버스는 2240 × 1600 px이지만 CSS는 변수화하여 추후 사이즈 변경이 한 곳에서 처리되도록 한다.

---

## 5. 파일명 매핑 규칙

**형식**: `{타입}_{연령}_{월}_{주차}.jpg`

| 카테고리 | 라벨 | 코드 |
|---|---|---|
| 타입 | STEAM WALL 활동사진 | `스팀월활동` |
| 타입 | 아트 활동사진 | `아트활동` |
| 연령 | 만1세 | `01세` |
| 연령 | 만2세 | `02세` |
| 월 | 1월 친구들과 놀아요 | `01월` |
| 월 | 2월 함께 자라요 | `02월` |
| 월 | 3월 어린이집이 좋아요 | `03월` |
| 월 | 4월 봄을 만나요 | `04월` |
| 월 | 5월 우리 가족이 좋아요 | `05월` |
| 월 | 6월 나를 알아요 | `06월` |
| 월 | 7월 여름을 만나요 | `07월` |
| 월 | 8월 동물이랑 놀아요 | `08월` |
| 월 | 9월 여러 가지 탈 것들 | `09월` |
| 월 | 10월 가을과 만나요 | `10월` |
| 월 | 11월 다양한 색과 모양 | `11월` |
| 월 | 12월 겨울과 만나요 | `12월` |
| 주차 | N주차 | `0N주` (1-4) |

**예시**:
- 만1세 + 5월 우리가족이 좋아요 + 3주차 + STEAM WALL 업로드 → `스팀월활동_01세_05월_03주.jpg`
- 만2세 + 7월 여름을 만나요 + 2주차 + 아트 업로드 → `아트활동_02세_07월_02주.jpg`

---

## 6. 라우팅 스펙

| URL | 동작 |
|---|---|
| `/` 또는 `/?page=main` | 메인 선택 화면 |
| `/?page=report&age=01세&month=05월&week=03주&steam=1&art=1` | 결과 화면 (새 탭) |

**쿼리 파라미터 키**:
- `page`: `main` (기본) \| `report`
- `age`: `01세` \| `02세`
- `month`: `01월` ~ `12월`
- `week`: `01주` ~ `04주`
- `steam`: `1` (STEAM WALL 업로드 있음) \| 없음
- `art`: `1` (Art 업로드 있음) \| 없음

**구현**: 메인 페이지의 "생성" 버튼은 검증 통과 후 `target="_blank"` HTML 앵커로 새 탭을 연다. 업로드 파일 자체는 새 탭에 전달되지 않지만, lookup 방식이라 플래그만 있으면 충분하다.

---

## 7. 디자인 토큰 (CSS 변수)

```css
:root {
  --canvas-width: 2240px;
  --canvas-height: 1600px;
  --bg-color: #f2f2f2;
  --primary-color: #5B5FCC;       /* 생성 버튼 보라색 (목업 기준) */
  --steam-green: #1A8470;          /* STEAM WALL 로고 색 */
  --button-border: #d0d0d0;
  --button-selected-bg: #5B5FCC;
  --button-selected-fg: #ffffff;
  --button-unselected-bg: #ffffff;
  --button-unselected-fg: #333333;
  --age-btn-w: 500px;     --age-btn-h: 100px;   --age-gap: 20px;
  --topic-btn-w: 330px;   --topic-btn-h: 100px; --topic-gap: 15px;
  --week-btn-w: 240px;    --week-btn-h: 100px;  --week-gap: 20px;
  --upload-w: 1020px;     --upload-h: 400px;
  --header-w: 2400px;     --header-h: 250px;
  --section-title-w: 1020px; --section-title-h: 100px;
}
```

---

## 8. 상태 관리 (session_state)

**메인 페이지 키**:
| 키 | 타입 | 기본값 |
|---|---|---|
| `selected_age` | str | `"01세"` |
| `selected_month` | str | `"03월"` |
| `selected_week` | str | `"01주"` |
| `steam_files` | list\[UploadedFile\] | `[]` |
| `art_files` | list\[UploadedFile\] | `[]` |
| `show_no_photo_warning` | bool | `False` |

**리포트 페이지**: session_state 의존 금지. 모든 정보는 `st.query_params`에서 읽는다(새 탭이라 메인 페이지 state 공유 안 됨).

---

## 9. ⚠️ Do Not Break (절대 깨지면 안 되는 규칙)

1. **파일명 매핑 규칙(섹션 5)을 절대 변경하지 말 것**. 이미 `/reports/`에 만들어진 파일과 1:1로 매칭되어야 한다.
2. **Lookup 방식 고수**: 어떤 형태로든 업로드된 사진을 합성/편집/표시하지 않는다. 단지 카테고리 플래그만 본다.
3. **단일 선택 보장**: 연령/월/주차 그룹 내에서 동시에 2개 이상 선택되는 상태가 만들어지면 안 된다.
4. **기본값 보장**: 메인 페이지 첫 진입 시 만1세 / 3월 어린이집이 좋아요 / 1주차가 반드시 선택된 상태여야 한다.
5. **새 탭 동작**: 생성 버튼은 현재 탭을 갈아치우면 안 된다. 반드시 새 탭을 연다.
6. **양쪽 미업로드 차단**: STEAM WALL과 Art 둘 다 비어 있으면 결과 화면으로 넘어가지 않는다.
7. **파일 누락 대응**: lookup된 jpg가 `/reports/`에 없으면 결과 화면에서 "해당 레포트가 준비되지 않았습니다" 메시지를 표시하되 앱이 죽지 않게 한다.
8. **Streamlit `pages/` 자동인식 금지**: 폴더 이름은 반드시 `pages_local/`을 쓴다.

---

## 10. 코딩 규칙

- 한국어 주석 OK. 함수/변수명은 영어.
- `pathlib.Path` 사용. 문자열 경로 금지.
- 모든 매핑은 `utils/mapping.py`의 dict 상수로 관리. 하드코딩 금지.
- CSS는 `utils/styling.py`에서 단일 함수로 주입.
- session_state 키는 `utils/state.py`에 상수로 선언하여 오타 방지.
- UI 사이즈는 반드시 CSS 변수로 표현 (재조정 가능성 대비).

---

## 11. 실행 명령

```bash
# 개발
streamlit run app.py

# 의존성
pip install -r requirements.txt
```

`requirements.txt`:
```
streamlit>=1.30
Pillow>=10.0
```

---

## 12. 변경 이력 정책

이 문서는 아키텍처 결정이 바뀔 때마다 업데이트한다. 각 Sprint 종료 시 BEHAVIOR.md에 회귀 테스트용 동작 명세를 추가한다.
