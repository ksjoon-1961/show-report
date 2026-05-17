# Claude Code 단계별 프롬프트 — Show_report 배포 자동화

> 짝지 문서: `deployment_guide.md`
> 사용 방법: 각 Stage의 프롬프트 블록 전체를 복사해서 Claude Code에 그대로 붙여넣기
> 프로젝트 위치: `E:\temp\4.Show_report`

---

## 전체 진행 흐름

```
[Stage 1] 프로젝트 분석 & 배포 파일 생성        (Claude Code)
    ↓
[Stage 2] 환경변수 분리 리팩토링               (Claude Code)
    ↓
[Stage M1] GitHub 저장소 생성                  (수동: 웹 UI)
    ↓
[Stage 3] Git 초기화 & README & Push          (Claude Code)
    ↓
[Stage M2] Supabase 프로젝트 생성              (수동: 웹 UI)
    ↓
[Stage 4] Supabase 통합 코드 작성              (Claude Code)
    ↓
[Stage 5] 배포 전 사전 검증                    (Claude Code)
    ↓
[Stage M3] Railway 배포                        (수동: 웹 UI)
    ↓
─── 운영 단계 ──────────────────────────────
[Stage 6] 배포 후 디버깅 도우미                (Claude Code, 오류 시)
[Stage 7] 업데이트 워크플로 자동화             (Claude Code, 1회)
```

---

## Stage 1. 프로젝트 분석 & 배포 설정 파일 생성

**사용 시점**: 최초 1회
**예상 소요**: 5~10분

````
# 작업: Show_report 프로젝트 배포 준비 파일 생성

## 목적
`E:\temp\4.Show_report` 프로젝트를 Railway 배포 가능 상태로 정비합니다.
이 단계에서는 **설정 파일 4종 생성**과 **하드코딩된 민감 정보 스캔**만 수행합니다.
(실제 환경변수 분리는 다음 단계에서 진행)

## 작업

### 1. 프로젝트 구조 분석
- 진입점 파일 식별 (app.py / main.py / streamlit_app.py 등)
- 사용 프레임워크 식별 (Streamlit / FastAPI / Flask)
- 모든 `.py` 파일을 스캔하여 import된 외부 패키지 목록 작성
  - 표준 라이브러리는 제외
  - 로컬 모듈 import는 제외

### 2. 배포 설정 파일 4종 생성

**`requirements.txt`** — import 분석 결과 기반으로 작성
- ⚠️ `pip freeze` 결과를 그대로 쓰지 말 것 (불필요한 패키지 다수 포함됨)
- Windows 전용 패키지는 자동 제외: `pywin32`, `pywinpty`, `pyreadline`, `pyreadline3`
- 버전은 현재 설치된 버전을 `==`로 고정
- `python-dotenv` 자동 추가 (다음 단계에서 사용)

**`runtime.txt`**:
```
python-3.11.9
```

**`Procfile`** (확장자 없음) — 프레임워크별:
- Streamlit:
  ```
  web: streamlit run {진입점} --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```
- FastAPI:
  ```
  web: uvicorn {모듈}:app --host 0.0.0.0 --port $PORT
  ```
- Flask:
  ```
  web: gunicorn {모듈}:app --bind 0.0.0.0:$PORT
  ```
  (gunicorn도 requirements.txt에 추가)

**`.gitignore`**:
```
__pycache__/
*.pyc
*.pyo
.env
.env.local
.venv/
venv/
env/
.streamlit/secrets.toml
*.log
.DS_Store
.idea/
.vscode/
*.sqlite
*.db
.pytest_cache/
.coverage
htmlcov/
```

### 3. 하드코딩된 민감 정보 스캔
다음 패턴을 모든 `.py` 파일에서 검색하여 보고:
- `api_key`, `apikey`, `API_KEY`, `secret`, `password`, `token` 변수에 직접 문자열 할당된 라인
- Supabase URL 패턴: `https://*.supabase.co`
- PostgreSQL 연결 문자열: `postgresql://`, `postgres://`
- 그 외 URL/키로 보이는 긴 문자열 (40자 이상의 base64/hex)

스캔 결과를 다음 형식으로 보고:
```
파일: {경로}
줄: {번호}
변수: {변수명}
타입: {SUPABASE_URL / API_KEY / DATABASE_URL / 기타}
```

## Do Not Break
- 기존 비즈니스 로직 코드는 **절대** 수정하지 않는다
- 기존 import 구조 유지
- 이미 존재하는 `requirements.txt`, `Procfile` 등이 있다면 백업 후 작성 (`{원본}.bak`)
- 진입점 파일이 여러 개로 보이면 사용자에게 확인 후 진행

## 검증 기준
- [ ] `requirements.txt`, `runtime.txt`, `Procfile`, `.gitignore` 4개 파일 모두 프로젝트 루트에 존재
- [ ] `Procfile`에 `$PORT` 변수 포함
- [ ] `requirements.txt`에 Windows 전용 패키지 없음
- [ ] `requirements.txt`에 `python-dotenv` 포함
- [ ] 하드코딩 민감 정보 스캔 결과 보고됨

## 결과물 보고
1. 식별된 프레임워크와 진입점 파일명
2. 생성된 4개 파일 경로
3. 하드코딩 민감 정보 발견 항목 전체 목록 (Stage 2 입력으로 사용)
````

---

## Stage 2. 환경변수 분리 리팩토링

**사용 시점**: Stage 1 완료 후
**예상 소요**: 10~15분 (코드 양에 따라)

````
# 작업: 하드코딩된 민감 정보를 환경변수로 분리

## 컨텍스트
Stage 1에서 식별된 하드코딩 민감 정보를 환경변수로 분리합니다.

## 작업

### 1. `.env` 템플릿 작성
프로젝트 루트에 `.env` 생성:
```
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@host:5432/postgres

# (그 외 Stage 1에서 식별된 변수)
```
실제 값은 비워두고 placeholder로 작성. 사용자가 Supabase 생성 후 직접 채울 예정.

### 2. `.env.example` 작성
`.env`와 동일한 구조이지만 모든 값을 빈 문자열 또는 placeholder로 작성.
이 파일은 Git에 커밋되어 다른 사용자에게 어떤 변수가 필요한지 안내하는 용도.

### 3. 진입점 파일 최상단 수정
```python
from dotenv import load_dotenv
load_dotenv()
```
- `load_dotenv()`는 다른 모듈 import보다 먼저 호출되어야 함
- 이미 로드된 환경변수는 덮어쓰지 않음 (Railway 환경변수가 우선)

### 4. 하드코딩 → 환경변수 치환
Stage 1 스캔 결과의 각 항목에 대해:
```python
# Before
SUPABASE_URL = "https://xxxxx.supabase.co"

# After
import os
SUPABASE_URL = os.environ["SUPABASE_URL"]
```

원칙:
- 필수 변수: `os.environ["KEY"]` (없으면 KeyError로 즉시 실패하게)
- 선택 변수: `os.environ.get("KEY", "기본값")`
- 변수명은 SCREAMING_SNAKE_CASE 표준

### 5. 에러 메시지 개선
필수 환경변수가 없을 때 친절한 메시지:
```python
def get_required_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"필수 환경변수 '{key}'가 설정되지 않았습니다. "
            f".env 파일 또는 Railway Variables를 확인하세요."
        )
    return value
```
주요 진입 지점에서 이 헬퍼를 사용.

## Do Not Break
- 함수 시그니처와 클래스 인터페이스 변경 금지
- import 순서 유지 (`load_dotenv()`만 최상단 추가)
- 환경변수 이름은 변경 후 사용자에게 보고 (Railway 등록 시 필요)
- `.env`는 절대 git에 추가되지 않도록 확인

## 검증 기준
- [ ] 코드 내 하드코딩된 API 키/URL/비밀번호 0건
- [ ] `.env`와 `.env.example` 두 파일 생성됨
- [ ] `.env`가 `.gitignore`에 포함되어 있음
- [ ] 진입점에서 `load_dotenv()` 호출됨
- [ ] (선택) `python {진입점}` 실행 시 정상 시작 또는 친절한 환경변수 에러

## 결과물 보고
1. 수정된 파일 경로 목록
2. 정의된 환경변수 전체 목록 (Railway 등록용 — 값 제외, 키 이름만):
   ```
   SUPABASE_URL
   SUPABASE_KEY
   SUPABASE_SERVICE_KEY
   DATABASE_URL
   ...
   ```
3. 사용자가 다음에 해야 할 작업 안내:
   - Stage M1 (GitHub 저장소 생성) 진행 안내
   - .env 파일에 실제 값 채워 넣기 (Stage M2 후)
````

---

## Stage M1. GitHub 저장소 생성 (수동)

**사용 시점**: Stage 2 완료 후
**예상 소요**: 2분

```
1. https://github.com/new 접속
2. Repository name: show-report
3. Visibility: Private
4. README/.gitignore/license 모두 추가하지 않음
5. "Create repository" 클릭
6. 저장소 URL 메모: https://github.com/{사용자명}/show-report
```

다음 Stage에서 이 URL이 필요합니다.

---

## Stage 3. Git 초기화 & README & Push

**사용 시점**: Stage M1 완료 후
**예상 소요**: 5분

````
# 작업: Git 초기화, README 작성, GitHub Push

## 컨텍스트
GitHub에 빈 저장소 `show-report`가 생성된 상태입니다.
저장소 URL: https://github.com/{사용자명}/show-report
(실제 사용자명으로 교체할 것)

## 작업

### 1. .gitignore 동작 사전 검증
```powershell
cd E:\temp\4.Show_report
```
다음 파일들이 존재하는지 확인:
- `.env` (있어야 함)
- `.gitignore` (있어야 함, `.env` 포함)

### 2. README.md 작성 (한국어)
프로젝트 루트에 다음 구조로 작성:

```markdown
# Show Report

## 개요
[프로젝트 소스 코드 분석 후 1~2 문단으로 작성]

## 기술 스택
- Frontend/Backend: [Streamlit/FastAPI 등]
- Database: Supabase (PostgreSQL)
- Hosting: Railway

## 로컬 실행
\`\`\`powershell
# 1. 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
# .env.example을 복사하여 .env 작성 후 실제 값 입력
Copy-Item .env.example .env
# .env 파일 편집

# 4. 실행
[프레임워크에 맞는 실행 명령]
\`\`\`

## 환경변수
`.env.example` 참고. 필요한 변수:
[Stage 2에서 식별된 환경변수 목록]

## 배포
- GitHub `main` 브랜치 push 시 Railway가 자동 배포
- 운영 URL: (Railway 도메인 발급 후 업데이트)

## 라이선스
사내 프로젝트
```

### 3. Git 초기화 및 첫 커밋

```powershell
cd E:\temp\4.Show_report

# 기존 .git 폴더가 있으면 사용자에게 확인 후 진행
git init
git add .
```

### 4. **반드시** Push 전에 다음 검증 실행:
```powershell
git status
```
스테이징 목록에서 다음 파일이 **없어야** 함:
- `.env`
- `.streamlit/secrets.toml`
- 그 외 민감 정보 파일

⚠️ 만약 `.env`가 스테이징되어 있다면 **즉시 중단**하고 `.gitignore`를 점검할 것:
```powershell
git rm --cached .env  # 스테이징에서 제거
```

### 5. 커밋 및 Push
```powershell
git commit -m "chore: initial commit - deployment-ready setup

- Add requirements.txt, runtime.txt, Procfile, .gitignore
- Extract hardcoded credentials to environment variables
- Add README.md with setup instructions"

git branch -M main
git remote add origin https://github.com/{사용자명}/show-report.git
git push -u origin main
```

`{사용자명}`은 사용자에게 입력 받거나, 대화 시작 시 명시된 값 사용.

## Do Not Break
- **`.env` 파일이 절대로 커밋되지 않도록** 한다 (git status 두 번 확인)
- Force push (`-f`, `--force`) 사용 금지
- 기존 `.git` 폴더가 있다면 백업 또는 사용자 확인 후 진행
- Personal Access Token이 필요하면 사용자에게 안내 (자동 생성 시도 금지)

## 검증 기준
- [ ] `.env`가 `git ls-files` 결과에 없음
- [ ] README.md 작성됨
- [ ] `git log` 확인 시 첫 커밋이 있음
- [ ] `git remote -v` 확인 시 origin이 GitHub 저장소를 가리킴
- [ ] GitHub 웹에서 저장소 접속 시 파일이 보임 (.env는 보이지 않음)

## 결과물 보고
1. GitHub 저장소 URL
2. 첫 커밋 해시 (`git rev-parse HEAD`)
3. 다음 Stage 안내 (Stage M2: Supabase 프로젝트 생성)
````

---

## Stage M2. Supabase 프로젝트 생성 (수동)

**사용 시점**: Stage 3 완료 후
**예상 소요**: 5분 (생성 대기 2분 포함)

```
1. https://supabase.com/dashboard → New Project
2. Name: show-report
3. Database Password: 강력한 비밀번호 설정 후 별도 보관
4. Region: Northeast Asia (Seoul)
5. Create new project (약 2분 대기)

6. 다음 4개 값을 .env 파일에 입력:

   [Settings → API]
   - Project URL          → SUPABASE_URL
   - anon public key      → SUPABASE_KEY
   - service_role secret  → SUPABASE_SERVICE_KEY

   [Settings → Database → Connection string (URI)]
   - Connection string    → DATABASE_URL
     ⚠️ [YOUR-PASSWORD] 부분을 위 3번 비밀번호로 교체
     ⚠️ 비밀번호 특수문자는 URL 인코딩 필요 (@ → %40, # → %23 등)

7. .env 저장 후 로컬에서 앱 실행 → Supabase 연결 확인
```

---

## Stage 4. Supabase 통합 코드 작성

**사용 시점**: Stage M2 완료 후 (선택 — 기존 코드가 이미 Supabase 사용 중이면 스킵)
**예상 소요**: 15~20분

````
# 작업: Supabase 통합 코드 및 스키마 작성

## 컨텍스트
Supabase 프로젝트가 생성되었고 .env에 4개 키가 모두 입력된 상태입니다.

## 사전 질문
작업 시작 전 사용자에게 다음을 확인:
1. 저장할 데이터 종류 (예: 보고서, 사용자 정보, 로그 등)
2. 인증 사용 여부 (Supabase Auth 사용 여부)
3. 기존 코드가 이미 데이터를 어딘가에 저장하고 있는지

## 작업

### 1. supabase 패키지 추가
`requirements.txt`에 추가:
```
supabase==2.10.0
```
(또는 최신 안정 버전)

### 2. `db/__init__.py`, `db/client.py` 생성

```python
# db/client.py
import os
from functools import lru_cache
from supabase import create_client, Client


@lru_cache(maxsize=1)
def get_client() -> Client:
    """공개 anon key 기반 클라이언트 (사용자 권한)"""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


@lru_cache(maxsize=1)
def get_service_client() -> Client:
    """service_role key 기반 클라이언트 (서버 전용, RLS 우회)"""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)
```

### 3. `db/schema.sql` 작성
사용자 답변(작업 사전 질문)을 기반으로 테이블 스키마 작성:

```sql
-- 예시: 보고서 저장 테이블
create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- updated_at 자동 갱신 트리거
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_reports_updated_at
  before update on reports
  for each row execute function update_updated_at_column();

-- RLS (필요 시)
-- alter table reports enable row level security;
-- create policy "..." on reports for select using (...);
```

### 4. 연결 테스트 스크립트 `scripts/test_supabase.py`

```python
"""Supabase 연결 테스트. 로컬 및 배포 환경 모두에서 사용 가능."""
from dotenv import load_dotenv
load_dotenv()

import os
import sys


def main():
    required = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"❌ 누락된 환경변수: {', '.join(missing)}")
        sys.exit(1)

    try:
        from db.client import get_client
        client = get_client()
        # 가벼운 쿼리로 연결 확인
        response = client.table("reports").select("id").limit(1).execute()
        print(f"✅ Supabase 연결 성공")
        print(f"   URL: {os.environ['SUPABASE_URL']}")
        print(f"   응답: {response}")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 5. 사용자 안내 메시지 출력
스크립트 실행 안내:
```
다음 명령으로 Supabase 연결을 확인하세요:

1. Supabase Dashboard → SQL Editor 에서 db/schema.sql 내용을 실행
2. 로컬에서 연결 테스트:
   python scripts/test_supabase.py
```

## Do Not Break
- 기존 코드의 데이터 처리 로직 변경 금지 (Supabase는 추가 백엔드로만 통합)
- `service_role key`는 절대 클라이언트 측 코드(Streamlit UI 컴포넌트 등)에 직접 노출 금지
- 기존 데이터 마이그레이션이 필요한 경우 사용자에게 별도 확인

## 검증 기준
- [ ] `requirements.txt`에 `supabase` 추가됨
- [ ] `db/client.py` 생성됨
- [ ] `db/schema.sql` 생성됨
- [ ] `scripts/test_supabase.py` 실행 시 성공 메시지 출력
- [ ] (사용자 확인) SQL Editor에서 스키마 실행 성공

## 결과물 보고
1. 생성된 파일 목록
2. 정의된 테이블 요약
3. 사용자에게 다음 단계 안내: Stage 5로 진행
````

---

## Stage 5. 배포 전 사전 검증

**사용 시점**: Stage 4 완료 후, Railway 배포 직전
**예상 소요**: 5~10분

````
# 작업: Railway 배포 전 사전 검증

## 목적
Railway 배포 전에 빌드/런타임 오류를 사전에 잡아내고,
Railway Variables에 등록할 환경변수 목록을 정리합니다.

## 작업

### 1. Procfile 검증
- 파일이 프로젝트 루트에 존재하는가?
- 확장자가 없는가? (`Procfile`, not `Procfile.txt`)
- `$PORT` 변수를 사용하는가? (고정 포트 사용 금지)
- 진입점 파일이 실제로 존재하는가?
- (Streamlit) `--server.address=0.0.0.0` 포함되어 있는가?
- (Streamlit) `--server.headless=true` 포함 권장

검증 실패 시 자동 수정 또는 명확한 수정 방법 안내.

### 2. requirements.txt 검증
다음을 체크:
- [ ] 모든 줄이 `package==version` 형식
- [ ] Windows 전용 패키지 없음: `pywin32`, `pywinpty`, `pyreadline*`, `colorama`(선택)
- [ ] 알려진 빌드 문제 패키지 확인: `psycopg2` (대신 `psycopg2-binary` 권장)
- [ ] `python-dotenv` 포함
- [ ] Supabase 사용 시 `supabase` 포함
- [ ] 중복 항목 없음

### 3. 로컬 PORT 시뮬레이션 테스트
실제 Railway 환경 흉내내기:
```powershell
$env:PORT="8080"
# Procfile의 web: 뒤 명령을 직접 실행
streamlit run app.py --server.port=$env:PORT --server.address=0.0.0.0
```
- 8080 포트에서 정상 시작되는가?
- http://localhost:8080 접속 시 화면이 보이는가?
- 5초 후 자동 종료 (또는 사용자에게 수동 종료 요청)

### 4. .env 누출 최종 점검
```powershell
git ls-files | Select-String "\.env"
```
출력이 비어 있어야 함. 만약 `.env`가 추적되고 있다면 **즉시 경고**.

### 5. Railway Variables 등록 안내 생성
사용자가 Railway에 그대로 복사할 수 있는 형식으로 출력:

```
============================================================
🚂 Railway Variables 등록 가이드
============================================================

다음 환경변수를 Railway Dashboard → Variables 탭에 등록하세요.
값은 로컬 .env 파일에서 복사하세요.

[Supabase]
SUPABASE_URL=<.env의 값>
SUPABASE_KEY=<.env의 값>
SUPABASE_SERVICE_KEY=<.env의 값>
DATABASE_URL=<.env의 값>

[프로젝트 고유 변수]
(Stage 1에서 발견된 다른 변수들)

============================================================
⚠️ 주의:
- PORT 변수는 Railway가 자동 주입하므로 추가하지 마세요
- 값을 입력할 때 따옴표(", ')는 포함하지 마세요
- service_role key는 service 백엔드 전용입니다
============================================================
```

### 6. 최종 체크리스트 출력
```
Railway 배포 준비 완료 ✓

[ ] Procfile 검증 통과
[ ] requirements.txt 검증 통과  
[ ] 로컬 PORT 시뮬레이션 성공
[ ] .env 누출 없음
[ ] 환경변수 등록 가이드 출력 완료

다음 단계: Stage M3 (Railway 배포) 진행
```

## Do Not Break
- 로컬 `.env` 파일의 **실제 값을 출력하지 않는다** (변수 이름만)
- 검증 단계이므로 코드/설정 수정은 명시적 동의 후에만 수행
- 사용자 동의 없이 git 명령 실행 금지 (status, ls-files 같은 읽기 전용은 OK)

## 검증 기준
- [ ] 위 1~6번 모든 검증 통과 보고

## 결과물 보고
검증 결과 요약 + Railway Variables 등록 가이드 출력
````

---

## Stage M3. Railway 배포 (수동)

**사용 시점**: Stage 5 완료 후
**예상 소요**: 5~10분 (빌드 대기 포함)

```
1. https://railway.app/dashboard → New Project
2. "Deploy from GitHub repo" 선택
3. 처음이라면 GitHub 권한 승인
4. show-report 저장소 선택 → 자동 빌드 시작

5. 빌드 진행 중에 환경변수 등록:
   - 서비스 클릭 → Variables 탭 → New Variable
   - Stage 5에서 출력한 가이드의 모든 변수 입력
   - PORT는 추가하지 않음 (자동 주입됨)

6. 환경변수 저장 후 자동 재배포 대기 (1~3분)

7. 도메인 발급:
   - 서비스 → Settings 탭 → Networking 섹션
   - Generate Domain 클릭
   - URL 메모: https://show-report-production.up.railway.app

8. 발급된 URL 접속하여 동작 확인

9. 오류 발생 시:
   - Deployments 탭 → 최신 배포 → View Logs
   - 로그 전체 복사 → Stage 6 프롬프트로 디버깅
```

---

## Stage 6. 배포 후 디버깅 도우미

**사용 시점**: 배포 오류 발생 시 (상시)
**예상 소요**: 5~30분 (오류 복잡도에 따라)

````
# 작업: Railway 배포 오류 진단 및 수정

## 입력
다음 두 가지를 함께 제공하세요:

1. **Railway 로그 전체** (Deployments → 최신 → View Logs에서 복사):
```
[여기에 로그 붙여넣기]
```

2. **증상**:
- 브라우저에서 본 화면 (스크린샷 또는 텍스트 메시지)
- HTTP 상태 코드 (예: 502, 503, 404)
- 빌드 단계 실패인지 / 런타임 크래시인지

## 작업

### 1. 로그 분석
- 빌드 단계 (Building) vs 런타임 단계 (Starting/Running) 구분
- 첫 번째로 발생한 에러 메시지 식별 (이후 에러는 파생일 가능성)
- 에러 발생 직전 마지막 정상 로그 확인

### 2. 알려진 패턴 매칭
다음 패턴을 우선 점검:

| 증상/로그 키워드 | 원인 | 해결 |
|---|---|---|
| `Address already in use` | $PORT 미사용 | Procfile에 `$PORT` 추가 |
| `ModuleNotFoundError: No module named 'X'` | requirements.txt 누락 | X를 추가 후 push |
| `KeyError: 'SUPABASE_URL'` | Railway Variables 누락 | Variables 등록 |
| `connection refused` / `could not connect` | DATABASE_URL 문제 | URL 인코딩, Supabase 상태 확인 |
| `pywin32` 빌드 실패 | Windows 패키지 포함 | requirements.txt에서 제거 |
| `psycopg2` 빌드 실패 | C 컴파일 필요 | `psycopg2-binary`로 교체 |
| `Application failed to respond` | 앱이 PORT를 안 듣고 있음 | `--server.address=0.0.0.0` 확인 |
| `streamlit: command not found` | streamlit 미설치 | requirements.txt 확인 |
| `pip install` 도중 무한 대기 | 의존성 충돌 | 버전 명세 점검 |

### 3. 진단 결과 보고
다음 형식으로:
```
## 진단
- 단계: 빌드 / 런타임
- 근본 원인: [한 문장]
- 영향 범위: [어떤 기능이 안 되는지]

## 수정안
- 수정 파일: {경로}
- 변경 내용: [구체적인 diff]

## 재배포 절차
1. 수정 사항 적용
2. git add . && git commit -m "fix: ..."
3. git push
4. Railway가 자동 재배포 (1~3분)
5. 동작 확인: {URL}
```

### 4. 수정 적용
사용자 승인 후 수정 코드를 실제 파일에 반영.

### 5. 후속 검증 안내
재배포 후 확인할 것:
- Railway Logs에서 새 에러 없음
- 발급된 URL 접속 시 정상 화면
- 핵심 기능(Supabase 연결 등) 동작 확인

## Do Not Break
- 비즈니스 로직 변경 없이 **배포 관련 설정만** 수정
- 변경 사항은 별도 커밋으로 분리 (`fix:` prefix 사용)
- 동일 오류가 반복되면 기존 수정안의 부작용을 의심하고 사용자에게 보고
- 임시방편(예: try-except로 에러 숨기기) 사용 금지

## 검증 기준
- [ ] 에러 근본 원인이 명시되었는가
- [ ] 수정안이 구체적인가 (어떤 파일, 어떤 줄)
- [ ] 재배포 절차가 명확한가
- [ ] 후속 검증 방법이 제시되었는가
````

---

## Stage 7. 업데이트 워크플로 자동화

**사용 시점**: 배포 안정화 후 1회 (선택)
**예상 소요**: 10분

````
# 작업: 일상 업데이트를 위한 자동화 스크립트 작성

## 목적
매번 동일한 git 명령을 입력하지 않고 한 줄로 업데이트할 수 있게 합니다.

## 작업

### 1. `scripts/deploy_update.ps1` 작성
```powershell
# 사용법: .\scripts\deploy_update.ps1 "변경 내용 요약"
# 예: .\scripts\deploy_update.ps1 "fix: report sorting bug"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

Write-Host "▶ 현재 변경사항 확인..." -ForegroundColor Cyan
git status --short

# .env 누출 차단
$stagedFiles = git diff --cached --name-only
if ($stagedFiles -match "\.env$" -and $stagedFiles -notmatch "\.env\.example$") {
    Write-Host "❌ .env 파일이 스테이징되어 있습니다. 중단합니다." -ForegroundColor Red
    exit 1
}

$allFiles = git status --porcelain
if ($allFiles -match "\.env$" -and $allFiles -notmatch "\.env\.example$") {
    Write-Host "⚠️  .env 파일에 변경사항이 있지만 .gitignore로 제외됩니다." -ForegroundColor Yellow
}

Write-Host "`n▶ Staging 및 커밋..." -ForegroundColor Cyan
git add .
git commit -m $Message

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 커밋할 변경사항이 없거나 커밋 실패" -ForegroundColor Red
    exit 1
}

Write-Host "`n▶ Push 중..." -ForegroundColor Cyan
git push

Write-Host "`n✅ Push 완료!" -ForegroundColor Green
Write-Host "Railway가 1~3분 후 자동 배포합니다." -ForegroundColor Green
Write-Host "진행 확인: https://railway.app/dashboard" -ForegroundColor Cyan
```

### 2. `scripts/check_deployment.ps1` 작성
```powershell
# 사용법: .\scripts\check_deployment.ps1
# Railway URL의 헬스체크 수행

param(
    [string]$Url = "https://show-report-production.up.railway.app"
)

Write-Host "▶ 헬스체크: $Url" -ForegroundColor Cyan

try {
    $start = Get-Date
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30
    $elapsed = (Get-Date) - $start
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 정상 (HTTP $($response.StatusCode))" -ForegroundColor Green
        Write-Host "   응답 시간: $([math]::Round($elapsed.TotalMilliseconds, 0))ms" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  비정상 응답 (HTTP $($response.StatusCode))" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 접속 실패: $_" -ForegroundColor Red
    Write-Host "   Railway 로그를 확인하세요" -ForegroundColor Yellow
}
```

### 3. `CHANGELOG.md` 작성 (Keep a Changelog 형식)
```markdown
# Changelog

이 프로젝트의 모든 변경사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따릅니다.

## [Unreleased]

## [1.0.0] - YYYY-MM-DD
### Added
- Initial deployment to Railway
- Supabase integration for data persistence
- Environment variable based configuration
```

### 4. `BRANCHING.md` 작성 (선택)
```markdown
# 브랜치 전략

## 브랜치 종류
- **main**: 운영 브랜치. Railway가 이 브랜치를 자동 배포
- **dev**: 개발 통합 브랜치. 검증 후 main으로 머지
- **feature/{기능명}**: 기능 단위 작업 브랜치

## 일반 작업 흐름
1. `git checkout -b feature/new-export dev`에서 작업
2. 작업 완료 후 `dev`로 PR
3. dev에서 검증 완료 후 `main`으로 머지 → 자동 배포

## 긴급 수정 (hotfix)
1. `git checkout -b hotfix/critical-bug main`
2. 수정 후 main, dev 모두에 머지
```

### 5. README.md에 사용법 추가
README.md의 "배포" 섹션에 다음 추가:
```markdown
## 업데이트 배포
\`\`\`powershell
.\scripts\deploy_update.ps1 "변경 내용 요약"
\`\`\`

## 헬스체크
\`\`\`powershell
.\scripts\check_deployment.ps1
\`\`\`
```

## Do Not Break
- 기존 git 워크플로와 충돌하지 않도록
- 스크립트는 안전장치 우선 (`.env` 누출 차단 필수)
- ExecutionPolicy 변경 같은 시스템 설정 변경 금지

## 검증 기준
- [ ] `deploy_update.ps1` 실행 시 .env 차단 동작 확인
- [ ] `check_deployment.ps1`로 헬스체크 성공
- [ ] `CHANGELOG.md` 초안 작성됨
- [ ] README.md에 스크립트 사용법 반영

## 결과물
- `scripts/deploy_update.ps1`
- `scripts/check_deployment.ps1`
- `CHANGELOG.md`
- (선택) `BRANCHING.md`
- README.md 업데이트
````

---

## 부록. Claude Code 사용 팁

### 프롬프트 전달 방식
- 각 Stage의 ` ```` ` 코드 블록 **전체**를 복사해서 Claude Code에 붙여넣기
- Claude Code가 알아서 작업을 분해하고 도구를 호출
- 중간에 사용자 확인이 필요한 부분은 Claude Code가 멈추고 물어봄

### 작업 중단/재개
- Claude Code 세션을 중단했다가 재개할 경우, 이전 단계에서 무엇을 완료했는지 명시하면 좋음:
  ```
  Stage 1, 2는 완료된 상태입니다. 이제 Stage 3을 진행합니다.
  
  [Stage 3 프롬프트 본문 붙여넣기]
  ```

### 오류 발생 시
- Stage 6 프롬프트를 사용하여 디버깅
- Railway 로그 전체를 함께 전달

### 진행 상황 추적
- 각 Stage 완료 후 다음을 commit message에 기록 권장:
  - `chore: complete stage 1 - deployment file generation`
  - `chore: complete stage 2 - env var extraction`
  - ...

---

**문서 버전**: v1.0
**연관 문서**: `deployment_guide.md`
