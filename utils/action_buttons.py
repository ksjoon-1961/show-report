"""결과 페이지의 4개 액션 버튼 HTML/JS 빌더.

build_combined_action_buttons_html(): 좌우 2컬럼 레이아웃용 공통 버튼 세트.
  버튼 순서: 저장(2.png) / 인쇄(1.png) / 공유(4.png) / 메인으로(1.png)
  iframe(components.html, height=150)으로 렌더링.
"""
import base64
import json
from pathlib import Path

from utils.asset_helper import ASSETS_DIR


# 버튼 설정: (한글 라벨, 아이콘 파일명, JS 함수명)
_BTN_CONFIG = [
    ("저장",    "2.png", "doSave"),
    ("인쇄",    "1.png", "doPrint"),
    ("공유",    "4.png", "doShare"),
    ("메인으로", "1.png", "doMain"),
]


def _data_uri(path: Path) -> str:
    """이미지 파일 → data URI 변환. 파일 없으면 빈 문자열."""
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix, "application/octet-stream")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _button_inner(action: str) -> str:
    """버튼 내부 콘텐츠. 아이콘 파일 있으면 이미지, 없으면 텍스트 fallback."""
    icon_path = ASSETS_DIR / _ICON_FILES[action]
    label = _LABELS[action]
    if icon_path.exists():
        uri = _data_uri(icon_path)
        return (
            f'<img src="{uri}" alt="{label}" />'
            f'<span class="action-btn-label">{label}</span>'
        )
    return f'<span class="action-btn-fallback">{label}</span>'


# CSS는 iframe 내부에서 독립적으로 정의 (parent CSS 변수 접근 불가)
_IFRAME_CSS = """
html, body {
    margin: 0; padding: 0; background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif;
}
.action-buttons-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 8px 0;
}
.action-btn-real {
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
    cursor: pointer;
    display: inline-flex;
    line-height: 0;
    transition: opacity 0.15s ease, transform 0.15s ease;
}
.action-btn-real:hover {
    opacity: 0.85;
    transform: translateY(-2px);
}
.action-btn-real:active { transform: translateY(0); opacity: 1; }
.action-btn-real img {
    display: block;
    width: auto;
    height: auto;
    max-width: 200px;
    max-height: 80px;
    margin: 0;
}
.action-btn-fallback {
    font-size: 16px; font-weight: 700; color: #333;
    padding: 10px 18px;
    background: #f0f0f0;
    border: 2px solid #d0d0d0;
    border-radius: 12px;
}
"""


def build_combined_action_buttons_html(report_jpg_paths: list) -> str:
    """좌우 2컬럼 레이아웃용 공통 4개 버튼 블록 HTML 반환.

    report_jpg_paths: 존재하는 리포트 jpg Path 목록 (저장 시 첫 번째 사용).
    st.components.v1.html(..., height=150)으로 렌더링할 것.
    """
    # 저장: 첫 번째 존재 파일 사용
    save_items = []
    for p in report_jpg_paths:
        if p and p.exists():
            save_items.append((str(p.name), _data_uri(p)))

    save_js_data = json.dumps(save_items, ensure_ascii=False)

    js = f"""
const SAVE_ITEMS = {save_js_data};

function getParentURL() {{
    try {{ return window.parent.location.href; }}
    catch(e) {{ return window.location.href; }}
}}

function doSave() {{
    if (!SAVE_ITEMS.length) {{
        alert('저장할 이미지가 없습니다.');
        return;
    }}
    // 브라우저의 동시 다운로드 차단을 피하기 위해 순차 저장 (500ms 간격)
    SAVE_ITEMS.forEach(function(item, idx) {{
        setTimeout(function() {{
            var a = document.createElement('a');
            a.href = item[1];
            a.download = item[0];
            document.body.appendChild(a);
            a.click();
            a.remove();
        }}, idx * 500);
    }});
}}

function doPrint() {{
    try {{ window.parent.print(); }}
    catch(e) {{ window.print(); }}
}}

function doMain() {{
    try {{
        var p = window.parent;
        // window.open()으로 열린 탭이면 opener(메인 탭)가 존재
        if (p.opener && !p.opener.closed) {{
            p.opener.focus();
            p.close();
        }} else {{
            p.location.href = '/';
        }}
    }} catch(e) {{
        try {{ window.top.location.href = '/'; }} catch(e2) {{}}
    }}
}}

async function doShare() {{
    var url = getParentURL();
    var title = '토들러 아트 활동 레포트';
    if (navigator.share) {{
        try {{
            await navigator.share({{title: title, url: url}});
            return;
        }} catch(e) {{
            if (e.name === 'AbortError') return;
        }}
    }}
    try {{
        await navigator.clipboard.writeText(url);
        alert('URL이 클립보드에 복사되었습니다.');
    }} catch(e) {{
        prompt('이 URL을 복사해주세요:', url);
    }}
}}
"""

    btn_configs = [
        ("저장",    "2.png", "doSave()"),
        ("인쇄",    "3.png", "doPrint()"),
        ("공유",    "4.png", "doShare()"),
        ("메인으로", "1.png", "doMain()"),
    ]

    btns_html = ""
    for label, icon_file, fn_call in btn_configs:
        icon_path = ASSETS_DIR / icon_file
        if icon_path.exists():
            uri = _data_uri(icon_path)
            inner = f'<img src="{uri}" alt="{label}" />'
        else:
            inner = f'<span class="action-btn-fallback">{label}</span>'
        btns_html += f'<button class="action-btn-real" onclick="{fn_call}" aria-label="{label}">{inner}</button>\n'

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{_IFRAME_CSS}</style>
</head>
<body>
<div class="action-buttons-row">
{btns_html}</div>
<script>{js}</script>
</body>
</html>"""


def build_action_buttons_html(report_jpg_path: Path) -> str:
    """단일 리포트 이미지에 딸린 4개 버튼 블록 HTML 반환.

    st.components.v1.html(..., height=140)로 렌더링할 것.
    """
    img_uri = _data_uri(report_jpg_path)
    filename = report_jpg_path.name

    js = f"""
const IMG_URI = {json.dumps(img_uri, ensure_ascii=False)};
const FILENAME = {json.dumps(filename, ensure_ascii=False)};

function getParentURL() {{
    try {{ return window.parent.location.href; }}
    catch(e) {{ return window.location.href; }}
}}

function doSave() {{
    if (!IMG_URI) {{
        alert('저장할 이미지가 없습니다.');
        return;
    }}
    const a = document.createElement('a');
    a.href = IMG_URI;
    a.download = FILENAME;
    document.body.appendChild(a);
    a.click();
    a.remove();
}}

function doPrint() {{
    try {{ window.parent.print(); }}
    catch(e) {{ window.print(); }}
}}

function doMain() {{
    try {{
        var p = window.parent;
        if (p.opener && !p.opener.closed) {{
            p.opener.focus();
            p.close();
        }} else {{
            p.location.href = '/';
        }}
    }} catch(e) {{
        try {{ window.top.location.href = '/'; }} catch(e2) {{}}
    }}
}}

async function doShare() {{
    const url = getParentURL();
    const title = '토들러 아트 활동 레포트';
    if (navigator.share) {{
        try {{
            await navigator.share({{title: title, url: url}});
            return;
        }} catch(e) {{
            if (e.name === 'AbortError') return;
        }}
    }}
    try {{
        await navigator.clipboard.writeText(url);
        alert('URL이 클립보드에 복사되었습니다.');
    }} catch(e) {{
        prompt('이 URL을 복사해주세요:', url);
    }}
}}
"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{_IFRAME_CSS}</style>
</head>
<body>
<div class="action-buttons-row">
<button class="action-btn-real" onclick="doSave()" aria-label="저장">{_button_inner("save")}</button>
<button class="action-btn-real" onclick="doPrint()" aria-label="인쇄">{_button_inner("print")}</button>
<button class="action-btn-real" onclick="doMain()" aria-label="메인">{_button_inner("main")}</button>
<button class="action-btn-real" onclick="doShare()" aria-label="공유">{_button_inner("share")}</button>
</div>
<script>{js}</script>
</body>
</html>"""
