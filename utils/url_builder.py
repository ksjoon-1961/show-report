"""결과 페이지 URL 빌드.

새 탭으로 결과 페이지를 열 때 사용하는 쿼리 파라미터 URL을 생성한다.
한글 코드(01세 등)는 URL 인코딩한다.
"""
from urllib.parse import quote


def build_report_url(age_code: str, month_code: str, week_code: str,
                     has_steam: bool, has_art: bool) -> str:
    """결과 페이지로 가는 상대 URL을 반환.

    예: ?page=report&age=01%EC%84%B8&month=05%EC%9B%94&week=03%EC%A3%BC&steam=1&art=1
    """
    params = [
        ("page", "report"),
        ("age", age_code),
        ("month", month_code),
        ("week", week_code),
    ]
    if has_steam:
        params.append(("steam", "1"))
    if has_art:
        params.append(("art", "1"))

    query = "&".join(f"{k}={quote(v)}" for k, v in params)
    return f"?{query}"
