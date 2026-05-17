"""CSS 인젝션. 디자인 토큰은 :root 변수로 집중 관리."""
import streamlit as st
import streamlit.components.v1 as components


_CSS = """
<style>
:root {
  /* --- 캔버스 --- */
  --canvas-width: 2240px;
  --canvas-height: 1600px;

  /* --- 색상 --- */
  --bg-color: #f2f2f2;
  --primary-color: #5B5FCC;
  --steam-green: #1A8470;
  --button-border: #d0d0d0;
  --button-selected-bg: #5B5FCC;
  --button-selected-fg: #ffffff;
  --button-unselected-bg: #ffffff;
  --button-unselected-fg: #333333;

  /* --- 사이즈 --- */
  --header-w: 2400px;
  --header-h: 250px;
  --section-title-w: 1020px;
  --section-title-h: 100px;
  --age-btn-w: 500px;     --age-btn-h: 50px;    --age-gap: 20px;
  --topic-btn-w: 330px;   --topic-btn-h: 50px;  --topic-gap: 15px;
  --week-btn-w: 240px;    --week-btn-h: 50px;   --week-gap: 20px;
  --upload-w: 1020px;     --upload-h: 240px;
}

/* 사이드바 + 기본 메뉴 숨김 */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none !important; height: 0 !important; }

/* html/body 기본 여백 제거 */
html, body { margin: 0 !important; padding: 0 !important; }

/* 기본 배경 */
.stApp {
  background-color: var(--bg-color);
  padding-top: 0 !important;
}

/* 모든 상단 컨테이너 여백 제거 */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

/* ★ 핵심: stVerticalBlock gap 제거
   CSS 주입 컴포넌트 + JS iframe 같은 보이지 않는 요소에
   gap 26.67px가 각각 적용되어 ~53px 상단 공백이 발생하는 근본 원인.
   CSS만으로는 부족하므로 아래 _GAP_FIX_JS와 병행 적용. */
[data-testid="stVerticalBlock"] {
  row-gap: 0 !important;
  gap: 0 !important;
}

/* block-container: Streamlit 1.30+에서 .main 클래스가 없으므로
   셀렉터를 .block-container로 직접 지정 */
.block-container {
  padding-top: 5px !important;
  padding-bottom: 2rem;
  max-width: var(--canvas-width);
}

/* --- 헤더 영역 --- */
.header-area {
  width: 100%;
  margin-bottom: 20px;
}
.header-area img {
  max-width: 100%;
  height: auto;
}

/* --- 섹션 타이틀 --- */
.section-title {
  margin: 25px 0 15px;
  height: auto;
  display: flex;
  align-items: center;
}
.section-title img { width: 100%; height: auto; }

/* --- 선택 카드 버튼 (Streamlit st.button) --- */
[data-testid="stButton"] > button {
  height: var(--age-btn-h) !important;
  border-radius: 12px !important;
  font-size: 18px !important;
  font-weight: 600 !important;
  transition: all 0.15s ease;
}

[data-testid="stButton"] > button[kind="primary"] {
  background-color: var(--button-selected-bg) !important;
  color: var(--button-selected-fg) !important;
  border: 2px solid var(--button-selected-bg) !important;
}

[data-testid="stButton"] > button[kind="secondary"] {
  background-color: var(--button-unselected-bg) !important;
  color: var(--button-unselected-fg) !important;
  border: 1px solid var(--button-border) !important;
}

[data-testid="stButton"] > button:hover {
  border-color: var(--primary-color) !important;
  transform: translateY(-1px);
}

/* --- 컬럼 갭 미세조정 --- */
[data-testid="stHorizontalBlock"] {
  gap: 15px;
}

/* --- 우측 컬럼 좌측 소폭 패딩 (스페이서 열이 주 간격을 담당) --- */
.block-container > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:last-child {
  padding-left: 20px !important;
}

/* --- 좌측 컬럼 우측 80px 패딩 (좌측 콘텐츠 폭 80px 축소) --- */
.block-container > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:nth-child(1) {
  padding-right: 80px !important;
}

/* --- 우측 컬럼 섹션 타이틀: 위치 조정 + 갤러리 박스와 간격 2px --- */
.block-container > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:last-child .section-title {
  margin-top: 20px !important;
  margin-bottom: 2px !important;
}

/* --- 우측 컬럼 섹션 타이틀 이미지 높이 제한 (20px 감소) --- */
.block-container > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:last-child .section-title img {
  max-height: 70px !important;
  width: auto !important;
}

/* --- 생활주제 버튼 행 간격 spacer --- */
/* 내부 div */
.month-row-gap {
  height: 10px !important;
  min-height: 10px !important;
  display: block !important;
  overflow: visible !important;
}
/* stMarkdown 래퍼 자체도 강제 — 빈 content 시 0으로 접히는 것 방지 */
[data-testid="stMarkdown"]:has(.month-row-gap) {
  height: 10px !important;
  min-height: 10px !important;
  overflow: visible !important;
}

/* --- 갤러리 상단 라인 (타이틀 바로 아래, 갤러리 좌/우/하단 border의 상단 역할) --- */
hr.gallery-top-line {
  display: block;
  width: calc(75% - 10px); /* col_gallery([3,1]) 비율과 근사, 10px 축소 */
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  border: none !important;
  border-top: 1.5px solid rgba(49, 51, 63, 0.3) !important;
  box-sizing: border-box;
}
[data-testid="stMarkdown"]:has(hr.gallery-top-line) {
  height: 2px !important;
  min-height: 2px !important;
  overflow: visible !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* --- 아트 섹션 상단 여백 spacer --- */
.art-section-gap {
  height: 10px !important;
  min-height: 10px !important;
  display: block !important;
  overflow: visible !important;
}
[data-testid="stMarkdown"]:has(.art-section-gap) {
  height: 10px !important;
  min-height: 10px !important;
  overflow: visible !important;
}

/* --- 파일 업로더 드롭존: 갤러리와 완전히 독립된 박스 --- */

/* 드롭존 외곽: 연한 그린 배경 */
[data-testid="stFileUploaderDropzone"] {
  min-height: 215px !important;
  max-height: 215px !important;
  width: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  position: relative !important;
  border: 1.5px solid rgba(26, 132, 112, 0.35) !important;
  border-radius: 10px !important;
  background: rgba(26, 132, 112, 0.13) !important;
}

/* 갤러리 컨테이너: margin-top으로 타이틀과 간격 확보 + border 선명도 강화 */
[data-testid="stVerticalBlockBorderWrapper"] {
  margin-top: 4px !important;
  border-color: rgba(49, 51, 63, 0.35) !important;
}

/* --- 갤러리 썸네일 삭제 버튼: 이미지 우측 상단 원형 오버레이 --- */

/* 썸네일 컬럼 내부: position relative 기준 */
div[data-testid="stColumn"]:has([data-testid="stImage"]) > div[data-testid="stVerticalBlock"] {
  position: relative;
}

/* 삭제 버튼 wrapper: 우측 상단 절대 위치 */
div[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stButton"] {
  position: absolute !important;
  top: 4px !important;
  right: 4px !important;
  width: auto !important;
  z-index: 20;
  margin: 0 !important;
  padding: 0 !important;
}

/* 삭제 버튼 실제: 작은 원형 반투명 */
div[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stButton"] > button {
  width: 22px !important;
  height: 22px !important;
  min-height: 22px !important;
  padding: 0 !important;
  border-radius: 50% !important;
  background: rgba(0, 0, 0, 0.5) !important;
  color: white !important;
  border: none !important;
  font-size: 12px !important;
  line-height: 1 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
div[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stButton"] > button:hover {
  background: rgba(0, 0, 0, 0.75) !important;
  transform: none !important;
  border-color: transparent !important;
}

/* 드롭존 내부 텍스트 완전 숨김 */
[data-testid="stFileUploaderDropzoneInstructions"] {
  display: none !important;
}

/* Browse files 버튼: 연한 그린 배경 */
[data-testid="stFileUploaderDropzone"] button {
  position: relative !important;
  z-index: 2 !important;
  background: rgba(26, 132, 112, 0.13) !important;
  border: 1.5px solid rgba(26, 132, 112, 0.35) !important;
  box-shadow: none !important;
  color: #1A8470 !important;
  font-size: 26px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  padding: 12px 10px !important;
  white-space: normal !important;
  max-width: 110px !important;
  text-align: center !important;
  line-height: 1.35 !important;
  border-radius: 10px !important;
}

/* 숨겨진 input[type="file"]을 드롭존 전체로 확장 (클릭·드롭 수신) */
[data-testid="stFileUploaderDropzone"] input[type="file"] {
  position: absolute !important;
  inset: 0 !important;
  width: 100% !important;
  height: 100% !important;
  opacity: 0 !important;
  cursor: pointer !important;
  z-index: 1 !important;
}

/* nonce 회전 직전 찰나의 파일 목록 깜박임 방지 */
[data-testid="stFileUploaderFileList"] {
  display: none !important;
}

/* --- 생성 버튼: 이미지 링크 (업로드 있음) --- */
.generate-img-link {
  display: block;
  text-decoration: none !important;
  margin: 25px auto 20px;
  max-width: 714px;
  cursor: pointer;
}
.generate-img-link img { display: block; width: 100%; height: auto; max-height: 72px; }
.generate-img-link:hover { opacity: 0.88; }

/* --- 생성 버튼: 비활성 이미지 (업로드 없음) --- */
.generate-img-disabled {
  max-width: 714px;
  margin: 25px auto 20px;
  opacity: 0.45;
  cursor: not-allowed;
}
.generate-img-disabled img { display: block; width: 100%; height: auto; max-height: 72px; }

/* ============================================================
   결과 페이지 — 레포트 박스
   ============================================================ */

/* 두 박스를 가로로 나란히: align-items:stretch 로 항상 같은 높이 유지 */
.reports-row {
  display: flex;
  gap: 20px;
  width: 95%;
  margin: 8px auto 20px;
  align-items: stretch;
  box-sizing: border-box;
}

/* 레포트 박스 — 이미지·미생성 공통 */
.report-box {
  flex: 1;
  border: 1.5px solid rgba(49, 51, 63, 0.3);
  border-radius: 12px;
  padding: 10px;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  overflow: hidden;
  min-width: 0;          /* flex 자식의 width 축소 허용 */
}

/* 이미지: 박스 폭에 꽉 채움 */
.report-box img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 6px;
}

/* 미생성 메시지: 상하좌우 가운데 */
.report-empty-msg {
  text-align: center;
  color: #aaa;
  font-size: 18px;
  font-weight: 500;
  line-height: 1.8;
  margin: 0;
}

/* ============================================================
   결과 페이지 (레거시 — 이전 Sprint 코드, 참조용 유지)
   ============================================================ */

/* 결과 페이지 헤더 */
.report-header {
  text-align: center;
  margin: 5px auto;
  padding-bottom: 25px;
  border-bottom: 3px solid var(--primary-color);
  max-width: 1800px;
}
.report-header h1 {
  margin: 0;
  color: #333;
  font-size: 38px;
}
.report-meta {
  color: var(--primary-color);
  font-size: 22px;
  font-weight: 700;
  margin: 15px 0 0;
}

/* 섹션 타이틀 (STEAM WALL 활동 / 아트 활동) */
.report-section-title {
  font-size: 26px;
  font-weight: 700;
  margin: 35px 0 18px;
  padding: 8px 16px;
  border-left: 8px solid var(--primary-color);
  color: #333;
}

/* 이미지 박스 */
.report-image-box {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin: 0 auto 24px;
  max-width: 1600px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.report-image-box img {
  border-radius: 8px;
  display: block;
}

/* 파일 누락 박스 */
.report-missing {
  background: #fff8e1;
  border: 2px solid #ffc107;
  border-radius: 16px;
  padding: 50px 30px;
  text-align: center;
  margin: 0 auto 30px;
  max-width: 1600px;
}
.report-missing-icon { font-size: 56px; margin-bottom: 16px; }
.report-missing-title {
  font-size: 22px; font-weight: 700; color: #856404; margin-bottom: 12px;
}
.report-missing-detail {
  font-size: 16px; color: #6c757d;
  font-family: 'Consolas', 'Courier New', monospace;
}

/* 액션 버튼 placeholder (Sprint 2 단계) */
.action-buttons-area {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 24px auto 50px;
  max-width: 1600px;
}
.action-btn-placeholder {
  width: 140px;
  height: 100px;
  background: #f0f0f0;
  border: 2px dashed #b0b0b0;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #666;
  text-align: center;
  line-height: 1.4;
}

/* 쿼리 오류 박스 */
.report-error-box {
  background: #ffebee;
  border: 2px solid #ef5350;
  border-radius: 16px;
  padding: 40px;
  margin: 60px auto;
  max-width: 800px;
  text-align: center;
}
.report-error-box h3 { color: #c62828; margin-top: 0; font-size: 26px; }
.report-error-box p {
  color: #555; font-size: 16px;
  font-family: 'Consolas', 'Courier New', monospace;
}

/* 메인으로 가기 링크 */
.back-to-main-link {
  display: inline-block;
  margin: 20px auto;
  padding: 14px 28px;
  background: var(--primary-color);
  color: white !important;
  text-decoration: none !important;
  border-radius: 10px;
  font-weight: 700;
  font-size: 16px;
}
.back-to-main-link:hover { opacity: 0.9; transform: translateY(-1px); }

/* 모든 미존재 시 정보 배너 */
.report-info-banner {
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  font-size: 18px;
  color: #1565c0;
  max-width: 1200px;
  margin: 30px auto;
}
.report-info-banner a { color: var(--primary-color); font-weight: 700; }

/* ============================================================
   인쇄용 CSS (Sprint 3)
   인쇄 시 UI 크롬을 모두 숨기고 리포트 이미지만 표시.
   ============================================================ */
@media print {
    .stApp, body, html {
        background: white !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* UI 크롬, 헤더, 액션 버튼 iframe 모두 숨김 */
    [data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    header[data-testid="stHeader"],
    #MainMenu,
    .report-header,
    .report-section-title,
    .report-missing,
    .report-info-banner,
    .report-error-box,
    .back-to-main-link,
    iframe[title*="components"],
    iframe[title*="streamlit"] {
        display: none !important;
    }

    /* 이미지 박스 장식 제거 */
    .report-image-box {
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        background: white !important;
        page-break-inside: avoid;
    }
    .report-image-box img {
        max-width: 100% !important;
        height: auto !important;
        display: block;
        margin: 0 auto;
    }

    /* 메인 컨테이너 패딩 제거 */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
}
</style>
"""

# st.markdown의 <script>는 React dangerouslySetInnerHTML 제약으로 실행되지 않음.
# components.html() iframe 안에서만 JS가 실제로 동작하므로 여기서 주입.
_GAP_FIX_JS = """<!DOCTYPE html>
<html>
<head><style>html,body{margin:0;padding:0;background:transparent;overflow:hidden;}</style></head>
<body>
<script>
(function() {
  var p = window.parent || window;

  /* ── 1회성: 부모 <head>에 <style> 직접 삽입 ──────────────────────────
     st.markdown CSS는 body 내부 div에 주입되어 일부 브라우저/Streamlit 버전에서
     전역 적용이 안 될 수 있음. head 주입은 항상 전역 적용된다. */
  try {
    if (!p.document.getElementById('ta-head-css')) {
      var s = p.document.createElement('style');
      s.id = 'ta-head-css';
      s.textContent = '';
      p.document.head.appendChild(s);
    }
  } catch(e) {}


  /* ── 반복 실행: gap·spacer·갤러리 border inline 강제 ─────────────── */
  function fixGap() {
    try {
      p.document.querySelectorAll('[data-testid="stVerticalBlock"]').forEach(function(el) {
        el.style.setProperty('gap', '0', 'important');
        el.style.setProperty('row-gap', '0', 'important');
      });
      p.document.querySelectorAll('section[data-testid="stMain"]').forEach(function(el) {
        el.style.setProperty('padding-top', '0', 'important');
      });
      p.document.querySelectorAll('[data-testid="stMarkdown"]').forEach(function(el) {
        if (el.querySelector('.month-row-gap')) {
          el.style.setProperty('height', '10px', 'important');
          el.style.setProperty('min-height', '10px', 'important');
          el.style.setProperty('overflow', 'visible', 'important');
        }
        if (el.querySelector('.art-section-gap')) {
          el.style.setProperty('height', '10px', 'important');
          el.style.setProperty('min-height', '10px', 'important');
          el.style.setProperty('overflow', 'visible', 'important');
        }
      });

      // ── gallery-top-line stMarkdown 래퍼 높이 강제 ──────────────────
      p.document.querySelectorAll('[data-testid="stMarkdown"]').forEach(function(el) {
        if (el.querySelector('hr.gallery-top-line')) {
          el.style.setProperty('height', '2px', 'important');
          el.style.setProperty('min-height', '2px', 'important');
          el.style.setProperty('overflow', 'visible', 'important');
          el.style.setProperty('padding', '0', 'important');
          el.style.setProperty('margin', '0', 'important');
        }
      });

      // ── 갤러리 border: 상단 라인이 top border 역할 → margin-top 불필요 ─
      p.document.querySelectorAll('[data-testid="stVerticalBlock"]').forEach(function(vb) {
        var cs = p.getComputedStyle(vb);
        if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') {
          vb.style.setProperty('box-shadow', 'none', 'important');
          vb.style.setProperty('border', '1.5px solid rgba(49,51,63,0.35)', 'important');
          vb.style.setProperty('border-radius', '8px', 'important');
          vb.style.setProperty('margin-top', '0', 'important');
        }
      });

      // ── 갤러리 삭제 버튼: stImage 내부로 이동 → 이미지 우측 상단 정확한 오버레이 ─
      p.document.querySelectorAll('div[data-testid="stColumn"]').forEach(function(col) {
        var imgDiv = col.querySelector('[data-testid="stImage"]');
        var btnDiv = col.querySelector('[data-testid="stButton"]');
        if (!imgDiv || !btnDiv || imgDiv.contains(btnDiv)) return;
        imgDiv.style.setProperty('position', 'relative', 'important');
        imgDiv.appendChild(btnDiv);
        btnDiv.style.setProperty('position', 'absolute', 'important');
        btnDiv.style.setProperty('top', '4px', 'important');
        btnDiv.style.setProperty('right', '4px', 'important');
        btnDiv.style.setProperty('z-index', '20', 'important');
        btnDiv.style.setProperty('margin', '0', 'important');
        btnDiv.style.setProperty('padding', '0', 'important');
        btnDiv.style.setProperty('width', 'auto', 'important');
        var btn = btnDiv.querySelector('button');
        if (btn) {
          btn.style.setProperty('width', '22px', 'important');
          btn.style.setProperty('height', '22px', 'important');
          btn.style.setProperty('min-height', '22px', 'important');
          btn.style.setProperty('padding', '0', 'important');
          btn.style.setProperty('border-radius', '50%', 'important');
          btn.style.setProperty('background', 'rgba(0,0,0,0.5)', 'important');
          btn.style.setProperty('color', 'white', 'important');
          btn.style.setProperty('border', 'none', 'important');
          btn.style.setProperty('font-size', '12px', 'important');
          btn.style.setProperty('line-height', '1', 'important');
          btn.style.setProperty('display', 'flex', 'important');
          btn.style.setProperty('align-items', 'center', 'important');
          btn.style.setProperty('justify-content', 'center', 'important');
        }
      });
    } catch(e) {}
  }

  fixGap();

  try {
    new MutationObserver(fixGap).observe(p.document.body, { childList: true, subtree: true });
  } catch(e) {}

  setInterval(fixGap, 500);
})();
</script>
</body>
</html>"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    components.html(_GAP_FIX_JS, height=0)
