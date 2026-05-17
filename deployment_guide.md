# 웹 프로그램 배포 가이드 — GitHub + Railway + Supabase

> 대상 프로젝트: `E:\temp\4.Show_report`
> 기준 프레임워크: Streamlit (FastAPI/Flask는 Procfile 한 줄만 교체)
> 작성 목적: 재사용 가능한 배포 표준 가이드

---

## Phase 0. 사전 체크리스트

배포 시작 전 다음을 확인합니다.

- [ ] GitHub 계정 로그인 가능
- [ ] Railway 계정 로그인 가능 (https://railway.app)
- [ ] Supabase 계정 로그인 가능 (https://supabase.com)
- [ ] 로컬에 Git 설치됨 → `git --version`
- [ ] 로컬에서 앱이 정상 실행됨 → `streamlit run app.py` 로 동작 확인
- [ ] 진입점 파일명 확정 (보통 `app.py` 또는 `main.py`)

---

## Phase 1. 로컬 프로젝트 정비

### 1-1. 프로젝트 폴더로 이동

```powershell
cd E:\temp\4.Show_report
```

### 1-2. 필수 파일 4종 생성

배포에 필요한 파일은 `requirements.txt`, `runtime.txt`, `Procfile`, `.gitignore` 입니다.

**① `requirements.txt` — 의존성 목록**

```powershell
pip freeze > requirements.txt
```

가상환경(venv)에서 실행하는 것이 좋습니다. 불필요한 패키지가 섞이지 않도록, 가능하면 손으로 정리하거나 `pipreqs` 같은 도구를 사용합니다.

> ⚠️ Windows 전용 패키지 (`pywin32`, `pywinpty` 등)가 있다면 반드시 제거합니다. Railway의 Linux 환경에서 빌드 실패 원인이 됩니다.

**② `runtime.txt` — Python 버전 고정**

```
python-3.11.9
```

**③ `Procfile` — 실행 명령 (확장자 없음)**

Streamlit 앱:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

FastAPI 앱:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

> 💡 `$PORT`는 Railway가 자동으로 주입합니다. 절대 고정 포트(8501 등)로 두면 안 됩니다.

**④ `.gitignore` — Git 추적 제외**

```
__pycache__/
*.pyc
.env
.venv/
venv/
.streamlit/secrets.toml
*.log
.DS_Store
.idea/
.vscode/
```

### 1-3. 환경변수 분리

Supabase URL/KEY를 코드에 하드코딩하지 않고 환경변수로 분리합니다.

**`.env` 파일 (로컬 전용, Git 추적 제외)**

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
DATABASE_URL=postgresql://...
```

**코드에서 읽기**

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 로컬 개발 시에만 .env 로드, Railway에서는 무시됨

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
```

`python-dotenv`를 `requirements.txt`에 추가합니다.

---

## Phase 2. GitHub 저장소 생성 및 푸시

### 2-1. GitHub에서 새 저장소 생성

1. https://github.com/new 접속
2. **Repository name**: `show-report` (소문자, 하이픈 권장)
3. **Private** 선택 (사내 데이터 가능성 고려)
4. README, .gitignore, License → 추가하지 않음 (로컬에 이미 있음)
5. **Create repository** 클릭

### 2-2. 로컬에서 Git 초기화 및 푸시

```powershell
cd E:\temp\4.Show_report
git init
git add .
git commit -m "Initial commit: Show Report app"
git branch -M main
git remote add origin https://github.com/{사용자명}/show-report.git
git push -u origin main
```

> 💡 푸시 시 인증 창이 뜨면 GitHub Personal Access Token을 사용합니다.
> (https://github.com/settings/tokens → `repo` 권한)

---

## Phase 3. Supabase 프로젝트 설정

### 3-1. 프로젝트 생성

1. https://supabase.com/dashboard 접속
2. **New Project** 클릭
3. **Name**: `show-report`
4. **Database Password**: 강력한 비밀번호 설정 후 **별도로 안전하게 보관**
5. **Region**: `Northeast Asia (Seoul)` 선택
6. **Create new project** → 약 2분 대기

### 3-2. 연결 정보 수집

대시보드에서 다음 4개 값을 메모합니다.

| 위치 | 항목 | 환경변수명 |
|---|---|---|
| Settings → API | Project URL | `SUPABASE_URL` |
| Settings → API | anon public key | `SUPABASE_KEY` |
| Settings → API | service_role secret | `SUPABASE_SERVICE_KEY` (서버 전용) |
| Settings → Database | Connection string (URI) | `DATABASE_URL` |

> ⚠️ `DATABASE_URL`의 `[YOUR-PASSWORD]` 부분을 3-1에서 설정한 비밀번호로 직접 교체합니다.
> 비밀번호에 특수문자가 있으면 URL 인코딩이 필요합니다 (`@` → `%40`, `#` → `%23`).

### 3-3. 테이블 생성 (필요 시)

**SQL Editor** 메뉴에서 필요한 테이블을 생성합니다. 예시:

```sql
create table reports (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  content text,
  created_at timestamptz default now()
);
```

RLS(Row Level Security)는 인증을 사용한다면 활성화합니다.

---

## Phase 4. Railway 배포

### 4-1. 새 프로젝트 생성

1. https://railway.app/dashboard 접속
2. **New Project** → **Deploy from GitHub repo** 선택
3. 처음이라면 Railway가 GitHub 저장소에 접근하도록 권한 승인
4. `show-report` 저장소 선택
5. Railway가 자동으로 빌드 시작 (Procfile/requirements.txt 자동 감지)

### 4-2. 환경변수 설정

배포된 서비스 클릭 → **Variables** 탭 → **New Variable**:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
DATABASE_URL=postgresql://...
```

> ⚠️ `PORT` 변수는 Railway가 자동 주입하므로 **추가하지 않습니다**.

환경변수를 저장하면 Railway가 자동으로 서비스를 재배포합니다.

### 4-3. 도메인 발급

1. 서비스 → **Settings** 탭 → **Networking** 섹션
2. **Generate Domain** 클릭
3. `show-report-production.up.railway.app` 형태의 URL 발급
4. 발급된 URL로 접속하여 동작 확인

### 4-4. 시작 명령 수동 지정 (필요 시)

Procfile이 자동 감지되지 않으면 **Settings → Deploy → Custom Start Command** 에 입력:

```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Phase 5. 동작 확인

다음 순서로 점검합니다.

1. **빌드 로그 확인**: Railway → **Deployments** 탭 → 최신 배포의 **View Logs** → 에러 없는지 확인
2. **앱 렌더링 확인**: 발급된 URL 접속 → 첫 화면이 정상적으로 뜨는지 확인
3. **Supabase 연결 확인**: DB를 사용하는 기능(조회/저장) 동작 시험
4. **모바일 접속 확인**: Wi-Fi 환경에서 휴대폰 브라우저로 접속 시험

오류 발생 시 Railway **Logs** 탭에서 실시간 로그를 확인합니다.

---

## Phase 6. 업데이트 워크플로

배포 후 코드를 수정할 때 다음 절차를 따릅니다.

### 6-1. 일반 업데이트 (코드 변경)

```powershell
cd E:\temp\4.Show_report
git add .
git commit -m "Update: 변경 내용 요약"
git push
```

- Railway가 `main` 브랜치 push를 자동 감지
- 약 1~3분 후 새 버전이 자동 배포됨
- 진행 상황은 Railway **Deployments** 탭에서 실시간 확인 가능

### 6-2. 환경변수만 변경

코드 변경 없이 Railway **Variables** 탭에서 값을 수정/추가하면 자동 재시작됩니다.

### 6-3. 의존성 추가

```powershell
pip install 새패키지
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add: 새패키지 dependency"
git push
```

### 6-4. 롤백 (이전 버전으로 복귀)

문제가 발생한 경우:

1. Railway → **Deployments** 탭
2. 정상 동작했던 이전 배포의 **⋯** 메뉴
3. **Redeploy** 클릭 → 즉시 이전 버전으로 복귀

### 6-5. 브랜치 기반 배포 (선택)

안정성을 높이려면 `dev` 브랜치에서 작업 후 `main`으로 머지하는 방식을 사용합니다.

```powershell
git checkout -b dev
# 작업 후
git push origin dev
# 검증 완료 후
git checkout main
git merge dev
git push origin main
```

---

## 부록 A. 자주 마주치는 이슈

**🔴 빌드는 성공했는데 앱이 안 뜸 (502 / Application failed to respond)**
- Procfile의 포트가 `$PORT`인지 확인 (Railway는 동적 포트 주입)
- `--server.address=0.0.0.0` 누락 시 외부 접속 불가
- Streamlit의 경우 `--server.headless=true` 추가도 권장

**🔴 Supabase 연결 실패**
- `DATABASE_URL`의 비밀번호 특수문자 URL 인코딩 확인 (`@` → `%40`)
- Supabase 프로젝트가 일시 정지(Pause) 상태인지 확인 (무료 플랜 7일 미사용 시)
- Project URL/KEY 오타 확인

**🔴 requirements.txt 빌드 실패**
- Windows 전용 패키지(`pywin32`, `pywinpty`) 포함 여부 확인 → 제거
- 패키지 버전 고정 (`==`) 권장
- 일부 패키지는 `apt` 의존성 필요 → `nixpacks.toml`로 해결

**🔴 첫 접속 시 매우 느림**
- Railway 무료 플랜은 sleep mode가 있어 콜드 스타트가 느림
- Hobby 플랜 ($5/월) 으로 업그레이드 시 항상 켜짐

**🔴 Streamlit 파일 업로드 크기 제한**
- `.streamlit/config.toml` 추가:
  ```toml
  [server]
  maxUploadSize = 200
  ```

---

## 부록 B. 재사용 체크리스트 (다음 프로젝트용)

다음 배포 시 이 가이드를 그대로 활용하려면 아래 표의 값만 교체합니다.

| 항목 | Show Report (현재) | 다음 프로젝트 |
|---|---|---|
| 로컬 프로젝트 폴더 | `E:\temp\4.Show_report` | |
| GitHub 저장소명 | `show-report` | |
| Supabase 프로젝트명 | `show-report` | |
| Railway 서비스명 | `show-report` | |
| 진입점 파일 | `app.py` | |
| 프레임워크 | Streamlit | |
| Procfile 명령 | `streamlit run app.py ...` | |

---

## 부록 C. 보안 체크리스트

배포 전 마지막 점검:

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는가?
- [ ] `git log` 또는 `git status`로 `.env`가 추적되지 않는지 확인
- [ ] `SUPABASE_SERVICE_KEY` 같은 민감 키가 코드에 하드코딩되어 있지 않은가?
- [ ] Supabase 테이블의 RLS 정책이 적절히 설정되었는가?
- [ ] GitHub 저장소가 의도한 가시성(Private/Public)으로 설정되어 있는가?

---

## 부록 D. 비용 참고

| 서비스 | 무료 플랜 | 유료 플랜 |
|---|---|---|
| GitHub | Private 저장소 무제한 | - |
| Railway | $5 크레딧/월 (Trial), 이후 사용량 기반 | Hobby $5/월 (상시 가동) |
| Supabase | 500MB DB, 1GB 스토리지, 50K MAU | Pro $25/월 |

> 💡 사내용 가이드 데모는 Railway Hobby + Supabase Free 조합이 합리적입니다.

---

**문서 버전**: v1.0
**최종 수정**: 2026-05
