# SPRINT_PLAN.md

> 토들러 아트 프로그램 활동 레포트 메이커 — MVP 4 Sprint 계획.

## 원칙

- 각 Sprint 종료 시 **실행 가능한 상태**여야 한다. (`streamlit run app.py`)
- 각 Sprint마다 **PROMPT.md**를 만들어 Claude Code에 핸드오프한다.
- 각 Sprint 종료 시 **BEHAVIOR.md**에 회귀 테스트용 동작 명세를 추가한다.
- "Do Not Break" 규칙(CLAUDE.md 섹션 9)은 모든 Sprint에서 유지된다.

---

## Sprint 0 — 스캐폴딩 + 라우팅

**목표**: 빈 뼈대 + 페이지 라우팅 + CSS 토큰. 실행 시 두 페이지 사이를 새 탭으로 오갈 수 있어야 한다.

### 산출물
- 폴더 구조 (CLAUDE.md 섹션 3과 일치)
- `app.py` — query_params 기반 라우터
- `pages_local/main_page.py` — 빈 placeholder ("메인화면" 텍스트만)
- `pages_local/report_page.py` — 빈 placeholder ("결과화면" + query_params 출력)
- `utils/mapping.py` — 전체 매핑 dict 완비
- `utils/filename.py` — 파일명 빌드 함수
- `utils/state.py` — session_state 상수 + `init_state()` 함수
- `utils/styling.py` — `inject_css()` 함수 (디자인 토큰 변수 포함)
- `requirements.txt`
- `README.md` — 실행 방법

### 인수 조건 (Acceptance Criteria)
- [ ] `streamlit run app.py` 실행 시 사이드바 없이 메인 placeholder 표시
- [ ] URL을 `/?page=report&age=01세&month=05월&week=03주&steam=1`로 직접 입력 시 결과 placeholder 표시
- [ ] 메인 placeholder에 "결과 페이지로 (테스트)" 링크 클릭 시 새 탭에서 결과 placeholder 열림
- [ ] `utils/mapping.py`의 양방향 lookup 함수가 모든 라벨/코드에 대해 동작
- [ ] CSS 변수가 `:root`에 모두 정의되어 있고, `body`에 배경색 `#f2f2f2` 적용됨

---

## Sprint 1 — 메인 페이지 UI 완성

**목표**: 메인 화면 풀 UI. 선택 동작 + 업로드 + 검증까지 동작하지만 결과 페이지는 아직 placeholder.

### 산출물
- 헤더 영역 (assets/header.png 표시; 없으면 텍스트 fallback)
- 좌측 컬럼:
  - 수업 연령 그룹 (만1세 / 만2세, 단일 선택, 카드 버튼)
  - 표준보육과정 생활주제 그룹 (12개, 3개씩 4행, 단일 선택)
  - 수업 주차 그룹 (1주차~4주차, 4개 한 행, 단일 선택)
- 우측 컬럼:
  - STEAM WALL 활동 사진 업로드 (드래그앤드롭, multi-file)
  - 아트 활동 사진 업로드 (드래그앤드롭, multi-file)
- 하단 "토들러 아트 프로그램 활동 레포트 생성" 버튼
- 기본 선택값 적용 (만1세 / 5월 우리가족이 좋아요 / 3주차)
- 양쪽 모두 미업로드 시 경고 다이얼로그 + 확인 시 닫기

### 인수 조건
- [ ] 첫 진입 시 만1세 / 5월 우리가족이 좋아요 / 3주차가 시각적으로 선택된 상태
- [ ] 각 그룹 내에서 다른 옵션 클릭 시 즉시 선택 이동, 동시 2개 선택 불가
- [ ] 선택된 버튼은 보라색 배경 + 흰색 글자, 비선택은 흰색 배경
- [ ] 업로드 영역에 드래그앤드롭으로 사진 추가 가능
- [ ] 양쪽 업로드 모두 비어있을 때 "생성" 클릭 → 경고 다이얼로그 표시, 확인 시 닫힘
- [ ] 한쪽이라도 업로드되어 있고 생성 클릭 → 새 탭으로 결과 페이지 placeholder 열림 (올바른 쿼리 파라미터 포함)

---

## Sprint 2 — 결과 페이지 lookup + 표시

**목표**: 결과 페이지가 실제로 동작. lookup 성공/실패 케이스 모두 처리.

### 산출물
- 결과 페이지에서 query_params 파싱
- `utils/filename.py`로 후보 파일명 생성
- `/reports/` 폴더에서 파일 존재 확인
- 존재하는 jpg를 화면에 표시 (steam과 art 둘 다 있으면 둘 다 표시)
- 파일 누락 시 친화적 메시지
- 잘못된 쿼리 파라미터 (age 없음 등) 시 안내 메시지 + 메인으로 돌아가는 링크
- 액션 버튼 영역 placeholder (4개 자리만)

### 인수 조건
- [ ] 메인에서 생성 클릭 → 새 탭에 해당 조합의 jpg가 표시됨
- [ ] STEAM WALL만 업로드 → 스팀월활동 jpg 1장 표시
- [ ] 양쪽 업로드 → 두 jpg 모두 표시 (스팀월활동 먼저)
- [ ] `/reports/`에 해당 파일이 없으면 "준비되지 않았습니다" 안내 + 앱 죽지 않음
- [ ] 쿼리 파라미터가 비정상이면 에러 안내 + 메인 이동 링크
- [ ] 결과 페이지에는 사이드바 없음

---

## Sprint 3 — 액션 버튼 + 폴리싱

**목표**: 4개 액션 버튼(저장/인쇄/메인/공유) 동작. 디자인 정교화. 전체 회귀 테스트.

### 산출물
- HTML+JS 커스텀 액션 버튼 블록 (assets의 4개 버튼 이미지 사용)
- 저장: 현재 표시 중인 jpg 다운로드
- 인쇄: `window.print()`
- 메인: 메인 화면으로 이동 (현재 탭)
- 공유: Web Share API + URL clipboard fallback
- 메인 페이지 디자인 정교화 (간격, 정렬, 폰트)
- BEHAVIOR.md 완성

### 인수 조건
- [ ] 저장 버튼 클릭 시 표시 중인 jpg가 다운로드됨
- [ ] 인쇄 버튼 클릭 시 브라우저 인쇄 다이얼로그 표시
- [ ] 메인 버튼 클릭 시 메인 화면으로 이동
- [ ] 공유 버튼 클릭 시 모바일에서 OS 공유시트, 데스크톱에서 URL 클립보드 복사 + 안내
- [ ] 양쪽 jpg가 표시될 때 각 이미지 아래에 4 버튼이 한 세트씩 또는 통합 한 세트로 배치 (디자인 확정 시 결정)
- [ ] CLAUDE.md의 "Do Not Break" 규칙 모두 통과
- [ ] BEHAVIOR.md에 모든 동작 시나리오 기록

---

## Sprint 종료 의식 (각 Sprint 공통)

1. `streamlit run app.py`로 수동 검증
2. 인수 조건 체크리스트 100% 통과 확인
3. BEHAVIOR.md 갱신
4. Git commit: `Sprint N: <목표 한 줄>`
5. 다음 Sprint PROMPT.md 작성

---

## MVP 이후 후보 (Backlog)

- 활동계획안 생성기와의 연동 (`plan_id` 공유 패턴 재사용)
- ChromaDB RAG 기반 자유 텍스트 검색으로 레포트 찾기
- 만3세 이상 연령 확장
- 다국어 (영어/중국어)
- 인쇄 시 워터마크/날짜 자동 삽입
- Railway/Supabase 배포 파이프라인
