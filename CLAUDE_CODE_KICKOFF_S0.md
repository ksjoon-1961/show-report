# CLAUDE_CODE_KICKOFF_S0.md

> Claude Code 세션의 **첫 메시지**로 붙여넣을 프롬프트.
> 작업 디렉토리에 CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md, PROMPT_S0.md가 있어야 합니다.

---

## 붙여넣을 프롬프트 (아래 블록 전체 복사)

```
당신은 "토들러 아트 프로그램 활동 레포트 메이커" 프로젝트의 Sprint 0를 수행합니다.

작업 디렉토리: 현재 위치 (cwd 기준)
이 디렉토리에 다음 4개 문서가 있습니다:
- CLAUDE.md
- ARCHITECTURE.md
- SPRINT_PLAN.md
- PROMPT_S0.md

## 절차

1. 위 4개 .md 파일을 다음 순서로 읽으세요:
   CLAUDE.md → ARCHITECTURE.md → SPRINT_PLAN.md → PROMPT_S0.md
   (특히 CLAUDE.md 섹션 5 파일명 매핑, 섹션 9 Do Not Break, PROMPT_S0.md 섹션 13 Do Not을 정확히 숙지)

2. 읽기를 마치면 한 줄로 출력하세요:
   "Sprint 0 시작: 스캐폴딩 + 라우팅"

3. PROMPT_S0.md의 섹션 1~11을 순서대로 실행해서 스캐폴딩을 완성하세요.
   - 코드는 PROMPT_S0.md에 명시된 내용을 그대로 사용 (임의로 리팩토링/추가 금지)
   - assets/와 reports/는 비어 있는 채로 .gitkeep만 두기
   - 한글 파일명/경로 처리에 UTF-8 일관성 유지

4. 자체 검증을 수행하고 결과를 보고에 포함하세요:

   (a) 매핑 카운트 확인:
   python -c "from utils.mapping import AGE_LABELS, MONTH_LABELS, WEEK_LABELS; print(len(AGE_LABELS), len(MONTH_LABELS), len(WEEK_LABELS))"
   기대값: 2 12 4

   (b) 파일명 빌드 확인:
   python -c "from utils.filename import build_filename; print(build_filename('스팀월활동','01세','05월','03주'))"
   기대값: 스팀월활동_01세_05월_03주.jpg

   (c) 기본값 확인:
   python -c "from utils.state import DEFAULT_AGE, DEFAULT_MONTH, DEFAULT_WEEK; print(DEFAULT_AGE, DEFAULT_MONTH, DEFAULT_WEEK)"
   기대값: 01세 05월 03주

   (d) Streamlit 부팅 테스트:
   Windows: start /B streamlit run app.py --server.headless true --server.port 8501
   5초 대기 후 http://localhost:8501 응답 확인. 확인 후 프로세스 종료.
   (응답 확인은 curl 또는 PowerShell의 Invoke-WebRequest 사용)

5. PROMPT_S0.md 섹션 13의 보고 형식대로 최종 보고하세요.

## 진행 규칙

- 코드 주석은 한국어 가능. 함수/변수명은 영어. 사용자 보고는 한국어.
- CLAUDE.md, ARCHITECTURE.md, SPRINT_PLAN.md는 참조 전용. 절대 수정 금지.
- PROMPT_S0.md 자체도 수정 금지.
- 기존 파일이 이미 존재하면 덮어쓰기 전 사용자 확인 요청.
- pip install은 requirements.txt에 명시된 streamlit과 Pillow 외에는 사용자 확인 필요.
- 폴더 삭제는 절대 금지.

## 예외 처리

- 자체 검증 (a)~(d) 중 하나라도 실패하면 즉시 중단하고 사용자에게 보고. 임의로 수정/추측해서 진행하지 말 것.
- 한글 import 또는 한글 파일명 관련 오류 발생 시 인코딩 환경(`PYTHONIOENCODING=utf-8`) 설정 안내 후 사용자 응답 대기.
- Streamlit 부팅이 실패하면 streamlit 버전(`streamlit version`)을 출력하고 사용자에게 보고.

시작하세요.
```
