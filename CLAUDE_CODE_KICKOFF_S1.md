# CLAUDE_CODE_KICKOFF_S1.md

> Claude Code 세션의 **첫 메시지**로 붙여넣을 프롬프트.
> Sprint 0이 완료된 상태에서 시작합니다.

---

## 붙여넣을 프롬프트 (아래 블록 전체 복사)

```
당신은 "토들러 아트 프로그램 활동 레포트 메이커" 프로젝트의 Sprint 1을 수행합니다.

작업 디렉토리: 현재 위치 (cwd 기준)
Sprint 0이 이미 완료되어 다음 파일들이 존재합니다:
- app.py, requirements.txt, README.md
- pages_local/{__init__,main_page,report_page}.py
- utils/{__init__,mapping,filename,state,styling}.py
- assets/ (.gitkeep만 있을 수 있음), reports/ (.gitkeep + 일부 jpg)
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, PROMPT_S0.md, PROMPT_S1.md

## 절차

1. 다음 순서로 문서를 읽으세요:
   CLAUDE.md → ARCHITECTURE.md (특히 ADR-003, ADR-005) → SPRINT_PLAN.md (Sprint 1 섹션) → PROMPT_S1.md
   기존 utils/state.py, utils/styling.py, pages_local/main_page.py도 함께 확인하세요.

2. 읽기를 마치면 한 줄 출력:
   "Sprint 1 시작: 메인 페이지 UI 완성"

3. PROMPT_S1.md의 섹션 1~6을 순서대로 실행하세요:
   - 섹션 2: utils/url_builder.py 신규 생성
   - 섹션 3: utils/asset_helper.py 신규 생성
   - 섹션 4: utils/styling.py 전면 교체
   - 섹션 5: pages_local/main_page.py 전면 재작성
   - 섹션 6: BEHAVIOR.md 신규 생성
   주의: PROMPT_S1.md 섹션 1의 "절대 수정 금지" 목록을 정확히 준수.

4. PROMPT_S1.md 섹션 7의 자체 검증 5가지를 실행하고 결과를 보고에 포함:
   (a) 3개 모듈 import 정상
   (b) url_builder 케이스 1 (양쪽 업로드)
   (c) url_builder 케이스 2 (Art만 업로드)
   (d) asset_helper fallback (이미지 없을 때 TEXT 출력)
   (e) Streamlit HTTP 200

5. PROMPT_S1.md 섹션 9의 보고 형식대로 최종 보고하세요.

## 진행 규칙

- 코드 주석은 한국어 가능. 함수/변수명은 영어. 사용자 보고는 한국어.
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, PROMPT_S0.md, PROMPT_S1.md는 참조 전용. 절대 수정 금지.
- 기존 파일 덮어쓰기 전 한 번만 사용자에게 확인 요청. 단, 다음 2개는 PROMPT_S1.md가 명시적으로 "전면 교체/재작성"을 요구하므로 자동 진행:
  · utils/styling.py
  · pages_local/main_page.py
- pip install 금지 (requirements.txt 변경 불가).
- 폴더 삭제 금지.
- assets/와 reports/의 기존 콘텐츠는 절대 건드리지 말 것.

## ADR 준수 (중요)

- ADR-003: 단일선택은 반드시 st.button + type="primary"|"secondary" 패턴.
  st.radio / st.checkbox / st.selectbox 사용 금지.
- ADR-005: 모든 사이즈는 utils/styling.py의 :root CSS 변수로.
  컴포넌트 내부에 픽셀값 하드코딩 금지.

## 예외 처리

- 자체 검증 (a)~(e) 중 하나라도 실패 시 즉시 중단하고 보고.
- @st.dialog가 작동하지 않으면 streamlit 버전을 확인 (1.34+ 필요).
  버전 부족 시 사용자에게 보고 후 응답 대기.
- 한글 import / 한글 URL 인코딩 관련 오류 시 즉시 중단하고 보고.

시작하세요.
```
