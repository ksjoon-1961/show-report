"""라벨(UI 표시) ↔ 코드(파일명) 양방향 매핑.

CLAUDE.md 섹션 5의 파일명 매핑 규칙과 1:1 일치해야 합니다.
이 파일은 Do Not Break 대상입니다.
"""

# --- 연령 ---
AGE_LABEL_TO_CODE: dict[str, str] = {
    "만1세": "01세",
    "만2세": "02세",
}
AGE_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in AGE_LABEL_TO_CODE.items()}
AGE_LABELS: list[str] = list(AGE_LABEL_TO_CODE.keys())  # 표시 순서 보존
AGE_CODES: list[str] = list(AGE_LABEL_TO_CODE.values())

# --- 표준보육과정 생활주제 (월) ---
# 표시 순서: 3월부터 시작 (보육 1년 기준)
MONTH_LABEL_TO_CODE: dict[str, str] = {
    "3월 어린이집이 좋아요": "03월",
    "4월 봄을 만나요": "04월",
    "5월 우리 가족이 좋아요": "05월",
    "6월 나를 알아요": "06월",
    "7월 여름을 만나요": "07월",
    "8월 동물이랑 놀아요": "08월",
    "9월 여러 가지 탈 것들": "09월",
    "10월 가을과 만나요": "10월",
    "11월 다양한 색과 모양": "11월",
    "12월 겨울과 만나요": "12월",
    "1월 친구들과 놀아요": "01월",
    "2월 함께 자라요": "02월",
}
MONTH_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in MONTH_LABEL_TO_CODE.items()}
MONTH_LABELS: list[str] = list(MONTH_LABEL_TO_CODE.keys())
MONTH_CODES: list[str] = list(MONTH_LABEL_TO_CODE.values())

# --- 주차 ---
WEEK_LABEL_TO_CODE: dict[str, str] = {
    "1주차": "01주",
    "2주차": "02주",
    "3주차": "03주",
    "4주차": "04주",
}
WEEK_CODE_TO_LABEL: dict[str, str] = {v: k for k, v in WEEK_LABEL_TO_CODE.items()}
WEEK_LABELS: list[str] = list(WEEK_LABEL_TO_CODE.keys())
WEEK_CODES: list[str] = list(WEEK_LABEL_TO_CODE.values())

# --- 타입 ---
TYPE_STEAM: str = "스팀월활동"
TYPE_ART: str = "아트활동"


def age_label_to_code(label: str) -> str:
    return AGE_LABEL_TO_CODE[label]


def age_code_to_label(code: str) -> str:
    return AGE_CODE_TO_LABEL[code]


def month_label_to_code(label: str) -> str:
    return MONTH_LABEL_TO_CODE[label]


def month_code_to_label(code: str) -> str:
    return MONTH_CODE_TO_LABEL[code]


def week_label_to_code(label: str) -> str:
    return WEEK_LABEL_TO_CODE[label]


def week_code_to_label(code: str) -> str:
    return WEEK_CODE_TO_LABEL[code]


# --- 검증 헬퍼 ---
def is_valid_age_code(code: str) -> bool:
    return code in AGE_CODE_TO_LABEL


def is_valid_month_code(code: str) -> bool:
    return code in MONTH_CODE_TO_LABEL


def is_valid_week_code(code: str) -> bool:
    return code in WEEK_CODE_TO_LABEL
