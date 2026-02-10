import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; text-decoration: underline;'>일&nbsp;&nbsp;일&nbsp;&nbsp;재&nbsp;&nbsp;고&nbsp;&nbsp;현&nbsp;&nbsp;황&nbsp;&nbsp;표</h1>", unsafe_allow_label=True)

# --- 상단: 데이터 입력 섹션 ---
st.subheader("데이터 입력 (엑셀 복사/붙여넣기)")
raw_data = st.text_area("엑셀의 '장치장, 곡종, 재고량' 컬럼 데이터를 복사해서 아래에 붙여넣으세요.", height=150, placeholder="예: A1  옥수수  1500")

# --- 데이터 처리 로직 ---
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

# --- 중단: 업데이트 버튼 섹션 ---
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("현황표 업데이트", help="상단 데이터를 하단 도면에 반영합니다."):
        if raw_data:
            # 텍스트 데이터를 데이터프레임으로 변환
            lines = [line.split() for line in raw_data.strip().split('\n')]
            df = pd.DataFrame(lines, columns=['장치장', '곡종', '재고량'])
            # 딕셔너리 형태로 변환하여 저장
            st.session_state.inventory_data = df.set_index('장치장').to_dict('index')
            # 업데이트 시간 기록
            now = datetime.now()
            st.session_state.last_updated = now.strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")
        else:
            st.warning("데이터를 입력해주세요.")

with col2:
    st.markdown(f"<br><b>{st.session_state.last_updated}</b>", unsafe_allow_label=True)

# --- 하단: 창고 도식화 섹션 ---
st.divider()

def draw_storage(name):
    """창고 유닛(사각형/원)을 그리는 함수"""
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": "0"})
    item = data.get("곡종", "-")
    qty = data.get("재고량", "0")
    
    # 천단위 컴마 처리
    try:
        qty_formatted = "{:,}".format(int(qty.replace(',', '')))
    except:
        qty_formatted = qty

    # 도형 내부 디자인 (HTML/CSS)
    content = f"""
    <div style="text-align: center; line-height: 1.2; padding: 5px;">
        <div style="color: blue; font-weight: bold; font-size: 14px;">{item}</div>
        <div style="color: black; font-weight: bold; font-size: 16px;">{qty_formatted}</div>
        <div style="color: green; font-size: 12px;">{name}</div>
    </div>
    """
    return content

# 창고 배치 (7열 구성)
# 행 구성: 동그라미행 -> 사각형행 -> 동그라미행 -> 사각형행 -> 동그라미행
rows = [
    {"type": "circle", "count": 6, "prefix": "C1-"},
    {"type": "rect", "count": 7, "prefix": "R1-"},
    {"type": "circle", "count": 6, "prefix": "C2-"},
    {"type": "rect", "count": 7, "prefix": "R2-"},
    {"type": "circle", "count": 6, "prefix": "C3-"}
]

for row_info in rows:
    cols = st.columns(7)
    for i in range(row_info["count"]):
        name = f"{row_info['prefix']}{i+1}"
        with cols[i]:
            border_radius = "50%" if row_info["type"] == "circle" else "5px"
            height = "100px"
            st.markdown(f"""
                <div style="border: 2px solid #333; border-radius: {border_radius}; 
                height: {height}; display: flex; align-items: center; justify-content: center; 
                background-color: #f9f9f9; margin-bottom: 10px;">
                    {draw_storage(name)}
                </div>
            """, unsafe_allow_html=True)

# 버튼 스타일 수정 (초록색 둥근 버튼)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        border-radius: 10px;
        border: None;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)
