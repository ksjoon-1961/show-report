# CLAUDE_CODE_KICKOFF_S3.md

> Claude Code 세션의 **첫 메시지**로 붙여넣을 프롬프트.
> Sprint 2까지 완료된 상태에서 시작합니다. **이번 Sprint로 MVP가 완성됩니다.**

---

## 붙여넣을 프롬프트 (아래 블록 전체 복사)

```
당신은 "토들러 아트 프로그램 활동 레포트 메이커" 프로젝트의 Sprint 3을 수행합니다. 이번 Sprint로 MVP가 완성됩니다.

작업 디렉토리: 현재 위치 (cwd 기준)
Sprint 0·1·2가 이미 완료되어 있습니다. 다음 자산이 존재합니다:
- app.py, requirements.txt, README.md
- pages_local/{main_page,report_page}.py (둘 다 실제 구현 완료, 단 액션 버튼은 placeholder)
- utils/{mapping,filename,state,styling,url_builder,asset_helper,report_loader}.py
- BEHAVIOR.md (Sprint 0·1·2 섹션 포함)
- assets/, reports/ (일부 콘텐츠)
- 모든 .md 문서 (CLAUDE/ARCHITECTURE/SPRINT_PLAN/PROMPT_S0~S3)

## 절차

1. 다음 순서로 문서를 읽으세요:
   CLAUDE.md (특히 섹션 9 Do Not Break 11개 모두) → ARCHITECTURE.md (특히 ADR-004 액션 버튼) → SPRINT_PLAN.md (Sprint 3) → PROMPT_S3.md → BEHAVIOR.md (Sprint 0·1·2 동작 명세)
   기존 pages_local/report_page.py, utils/styling.py, utils/asset_helper.py(ASSETS_DIR 위치)도 함께 확인하세요.

2. 읽기를 마치면 한 줄 출력:
   "Sprint 3 시작: 액션 버튼 + 폴리싱"

3. PROMPT_S3.md의 섹션 1~5를 순서대로 실행하세요:
   - 섹션 2: utils/action_buttons.py 신규 생성
   - 섹션 3: pages_local/report_page.py 부분 수정 (import 추가 + 함수 1개 교체 + 호출부 1줄 변경 + 구 placeholder 함수 제거)
   - 섹션 4: utils/styling.py 끝에 @media print 블록 추가 (기존 CSS 유지!)
   - 섹션 5: BEHAVIOR.md 끝에 Sprint 3 섹션 + MVP 완료 회고 섹션 추가 (기존 섹션 유지!)
   주의: PROMPT_S3.md 섹션 1의 "절대 수정 금지" 목록을 정확히 준수.

4. PROMPT_S3.md 섹션 6의 자체 검증을 모두 실행하고 결과를 보고에 포함:
   - 6-1: 모듈 import 2개
   - 6-2: _verify_s3.py 작성 → 실행 → 모든 checks PASS 확인 → 파일 삭제
   - 6-3: Streamlit HTTP 200
   - 6-4: Sprint 0·1·2 회귀 검증 4종 (매핑/파일명/URL빌더/report_loader)

5. PROMPT_S3.md 섹션 8의 보고 형식대로 최종 보고하세요.

## 진행 규칙

- 코드 주석은 한국어 가능. 함수/변수명은 영어. 사용자 보고는 한국어.
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, PROMPT_S0~S3는 참조 전용. 절대 수정 금지.
- 다음 파일은 PROMPT_S3.md가 명시적으로 "기존 보존 + 추가"를 지시하므로 기존 내용 유지하면서 추가만:
  · utils/styling.py (기존 _CSS의 </style> 바로 앞에 @media print 블록 append)
  · BEHAVIOR.md (기존 Sprint 0·1·2 섹션 끝에 Sprint 3 + MVP 회고 append)
- pages_local/report_page.py는 부분 수정 (전면 재작성 아님):
  · 상단 import 2줄 추가
  · _render_action_placeholder 함수 → _render_action_buttons로 교체
  · _render_report_item 내부 호출 1줄 변경
  · 기타 코드(헬퍼, render() 진입점)는 그대로 유지
- pip install 금지 (requirements.txt 변경 불가).
- /reports/와 /assets/의 파일은 절대 삭제/이동/이름변경 금지.
- _verify_s3.py는 검증 직후 반드시 삭제.

## ADR 준수 (중요)

- ADR-001 Lookup 방식: 액션 버튼이 사용자 업로드 사진을 건드리면 안 됨. /reports/의 jpg만 처리.
- ADR-004 액션 버튼 HTML/JS 커스텀 블록:
  · st.button / st.download_button 사용 금지
  · st.components.v1.html(html, height=140)로 iframe 격리
  · iframe 내부 JS는 window.parent로 부모 페이지 제어
- ADR-002 새 탭 라우팅 유지: "메인" 버튼은 현재 탭에서 / 로 이동 (새 탭 X)

## CSS 추가 시 주의

- utils/styling.py의 기존 CSS는 절대 수정/삭제 금지. 새 @media print 블록은 </style> 바로 앞에 추가.
- @media print 규칙은 인쇄 시에만 적용되므로 화면 표시에는 영향 없음 (회귀 위험 낮음).
- 기존 .action-buttons-area, .action-btn-placeholder 클래스 CSS는 그대로 유지 (더 이상 사용되지 않지만 무해).

## 예외 처리

- 자체 검증 (6-2)의 checks 중 하나라도 실패 시 즉시 중단하고 보고.
- "한글 다운로드 파일명" 검증 실패 시 인코딩 환경 점검 후 보고 (PYTHONIOENCODING=utf-8).
- _verify_s3.py에서 "reports/스팀월활동_01세_07월_02주.jpg" 파일 누락 시 즉시 보고 (Sprint 2까지의 가정이 깨진 상태).
- Streamlit 부팅 실패 시 streamlit 버전(`streamlit version`)과 함께 보고.
- 회귀 검증 (6-4)에서 실패가 나오면 어느 Sprint의 동작이 깨졌는지 명시 후 보고.

## 통합 시나리오 (참고)

자체 검증 통과 후, 사용자가 수동으로 다음 8단계 시나리오를 시험할 예정입니다. 보고서에 이 시나리오를 명시해주세요:

1. 메인 화면 기본값 표시
2. 선택 + 양쪽 사진 업로드 + 생성
3. 새 탭에서 두 jpg + 8개 버튼 표시
4. 저장 → 다운로드
5. 인쇄 → 미리보기에 이미지만 표시
6. 공유 → 클립보드 복사 알림
7. 메인 → 메인 화면 복귀
8. assets/에 아이콘 배치 시 텍스트 → 이미지 전환

시작하세요.
```
