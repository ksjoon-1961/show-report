# STEAM WALL 토들러 아트 프로그램 활동 레포트 메이커

어린이집/유치원 교사가 연령·생활주제·주차를 선택하고 활동 사진을 업로드하면,
미리 제작된 활동 레포트 이미지를 조회하여 저장·인쇄·공유하는 Streamlit 웹 앱.

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 배포 (Railway)

1. Railway 프로젝트 생성 후 이 저장소 연결
2. 별도 환경변수 설정 불필요 (외부 서비스 미사용)
3. `Procfile`과 `runtime.txt`가 자동 인식됨

## URL 구조

| URL | 동작 |
|---|---|
| `/` | 메인 선택 화면 |
| `/?page=report&age=01세&month=05월&week=03주&steam=1&art=1` | 결과 화면 (새 탭) |

## 폴더 구조

```
app.py                  # 진입점 + 쿼리 파라미터 라우터
pages_local/            # 메인/결과 페이지 렌더러
utils/                  # 매핑·파일명·상태·스타일 헬퍼
assets/                 # UI 이미지
reports/                # 미리 제작된 레포트 jpg
```

## 문서

- `CLAUDE.md` — 프로젝트 컨텍스트 및 규칙
- `ARCHITECTURE.md` — 아키텍처 결정 기록
