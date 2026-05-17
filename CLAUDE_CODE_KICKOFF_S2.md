# CLAUDE_CODE_KICKOFF_S2.md

> Claude Code 세션의 **첫 메시지**로 붙여넣을 프롬프트.
> Sprint 1까지 완료된 상태에서 시작합니다.

---

## 붙여넣을 프롬프트 (아래 블록 전체 복사)

```
당신은 "토들러 아트 프로그램 활동 레포트 메이커" 프로젝트의 Sprint 2를 수행합니다.

작업 디렉토리: 현재 위치 (cwd 기준)
Sprint 0·1이 이미 완료되어 있습니다. 다음 자산이 존재합니다:
- app.py, requirements.txt, README.md
- pages_local/{main_page,report_page}.py (main_page는 완성, report_page는 placeholder)
- utils/{mapping,filename,state,styling,url_builder,asset_helper}.py
- BEHAVIOR.md (Sprint 0·1 섹션 포함)
- assets/ (일부 이미지 또는 비어있음), reports/ (스팀월활동_01세_07월_02주.jpg, 아트활동_01세_07월_02주.jpg 포함)
- 모든 .md 문서

## 절차

1. 다음 순서로 문서를 읽으세요:
   CLAUDE.md → ARCHITECTURE.md (특히 ADR-001 Lookup, ADR-002 라우팅) → SPRINT_PLAN.md (Sprint 2 섹션) → PROMPT_S2.md
   기존 pages_local/report_page.py, utils/filename.py, utils/styling.py도 함께 확인하세요.

2. 읽기를 마치면 한 줄 출력:
   "Sprint 2 시작: 결과 페이지 lookup + 표시"

3. PROMPT_S2.md의 섹션 1~5를 순서대로 실행하세요:
   - 섹션 2: utils/report_loader.py 신규 생성
   - 섹션 3: pages_local/report_page.py 전면 재작성 (placeholder 교체)
   - 섹션 4: utils/styling.py 끝부분에 결과 페이지 CSS 추가 (기존 CSS 유지!)
   - 섹션 5: BEHAVIOR.md 끝에 Sprint 2 섹션 추가 (기존 Sprint 0·1 섹션 유지!)
   주의: PROMPT_S2.md 섹션 1의 "절대 수정 금지" 목록을 정확히 준수.

4. PROMPT_S2.md 섹션 6의 자체 검증을 모두 실행하고 결과를 보고에 포함:
   - 6-1: 모듈 import 2개
   - 6-2: _verify_s2.py 작성 → 실행 → 결과 확인 → 파일 삭제 (9개 케이스 모두 PASS여야 함)
   - 6-3: Streamlit 부팅 + HTTP 200 확인

5. PROMPT_S2.md 섹션 8의 보고 형식대로 최종 보고하세요.

## 진행 규칙

- 코드 주석은 한국어 가능. 함수/변수명은 영어. 사용자 보고는 한국어.
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, PROMPT_S0~S2는 참조 전용. 절대 수정 금지.
- 다음 2개 파일은 PROMPT_S2.md가 명시적으로 "추가"를 지시하므로 기존 내용 보존 + 추가만:
  · utils/styling.py (기존 CSS 끝에 새 블록 append)
  · BEHAVIOR.md (기존 Sprint 0·1 섹션 끝에 Sprint 2 섹션 append)
- pages_local/report_page.py는 "전면 재작성" 지시이므로 그대로 교체.
- pip install 금지 (requirements.txt 변경 불가).
- /reports/와 /assets/의 파일은 절대 삭제/이동/이름변경 금지.
- _verify_s2.py는 검증 직후 반드시 삭제.

## ADR 준수 (중요)

- ADR-001 Lookup 방식: 업로드된 사진 자체를 표시하려는 시도 절대 금지.
  결과 페이지는 query_params + reports/ 파일만 사용.
- ADR-002 새 탭 라우팅: query_params만으로 결과 페이지가 동작해야 함.
  메인 페이지의 session_state에 접근하지 말 것.

## CSS 추가 시 주의

- utils/styling.py의 _CSS 변수에 있는 기존 CSS는 모두 그대로 유지.
- 추가할 위치: 기존 </style> 태그 바로 앞.
- 기존 :root 변수와 클래스를 활용 (var(--primary-color) 등).
- 새로운 CSS 변수는 추가하지 말 것 (필요하면 보고에 적고 사용자 결정 대기).

## 예외 처리

- 자체 검증의 C1~C9 중 하나라도 실패 시 즉시 중단하고 보고.
  - C1~C3 실패 → reports/ 파일 누락 가능성 → 실제 파일 목록을 보고에 첨부
  - C5~C9 실패 → load_from_query_params 로직 점검
- Streamlit 부팅 실패 시 즉시 보고.
- 한글 URL 인코딩 관련 오류 발생 시 PowerShell의 Invoke-WebRequest로 시도하거나, 부팅만 확인하는 방식으로 대체.
- 임의 폴백 로직 추가 금지. 명세에 없는 동작은 추가하지 말 것.

시작하세요.
```
