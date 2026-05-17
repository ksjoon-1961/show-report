"""assets/ 폴더의 이미지를 HTML img 태그로 반환.

이미지 파일이 없으면 텍스트 fallback을 반환한다.
앱이 죽지 않도록 보장하기 위함 (Do Not Break #7과 같은 정신).
"""
import base64
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _to_data_uri(path: Path) -> str:
    """Streamlit의 정적 서빙 제약을 피하기 위해 data URI로 인라인."""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def img_or_text(filename: str, fallback_text: str,
                width: str = "auto", height: str = "auto",
                css_class: str = "") -> str:
    """이미지가 있으면 <img>, 없으면 fallback 텍스트 HTML 반환.

    width/height는 CSS 값 (예: "1020px", "100%", "auto").
    """
    path = ASSETS_DIR / filename
    cls_attr = f' class="{css_class}"' if css_class else ""

    if path.exists():
        src = _to_data_uri(path)
        return (f'<img src="{src}" '
                f'style="width:{width};height:{height};object-fit:contain;"'
                f'{cls_attr} alt="{fallback_text}" />')
    else:
        return (f'<div style="width:{width};height:{height};'
                f'display:flex;align-items:center;justify-content:left;'
                f'font-size:24px;font-weight:bold;color:#333;"'
                f'{cls_attr}>{fallback_text}</div>')
