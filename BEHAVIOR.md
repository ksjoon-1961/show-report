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
