import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(layout="wide")

# --- [상단] 데이터 입력 섹션 ---
st.subheader("데이터 입력 (엑셀 복사/붙여넣기)")
raw_data = st.text_area("엑셀의 '장치장, 곡종, 재고량' 데이터를 붙여넣으세요.", height=150)

# --- 데이터 저장소 설정 ---
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

# --- [중단] 업데이트 버튼 및 시간 (중앙 배치) ---
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            border-radius: 15px;
            font-weight: bold;
            width: 100%;
            height: 50px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("현황표 업데이트"):
        if raw_data:
            try:
                lines = [line.split() for line in raw_data.strip().split('\n')]
                valid_lines = [l for l in lines if len(l) >= 3]
                df = pd.DataFrame(valid_lines).iloc[:, :3]
                df.columns = ['장치장', '곡종', '재고량']
                st.session_state.inventory_data = df.set_index('장치장').to_dict('index')
                st.session_state.last_updated = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")
                st.rerun() 
            except:
                st.error("데이터 형식 에러")
    
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 10px;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 (회색 박스 및 입체 배치) ---
st.markdown("<br>", unsafe_allow_html=True)

def get_content(name):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": "0"})
    item = data.get("곡종", "-")
    qty = str(data.get("재고량", "0"))
    try:
        qty_formatted = "{:,}".format(int(float(qty.replace(',', '')))) # 소수점 제거 및 컴마
    except:
        qty_formatted = "0"
    return f'<div style="color: blue; font-weight: bold; font-size: 13px;">{item}</div><div style="color: black; font-weight: bold; font-size: 15px;">{qty_formatted}</div><div style="color: green; font-size: 11px;">{name}</div>'

# 구조 설계
layout_rows = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)], "offset": "45px"},
    {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)], "offset": "0px"},
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)], "offset": "45px"},
    {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)], "offset": "0px"},
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)], "offset": "45px"}
]

# 전체를 감싸는 회색 박스 시작
html_drawing = f"""
<div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 40px; border-radius: 10px; min-width: 850px;">
    <h1 style="text-align: center; text-decoration: underline; font-weight: bold; margin-bottom: 40px;">
        일&nbsp;&nbsp;일&nbsp;&nbsp;재&nbsp;&nbsp;고&nbsp;&nbsp;현&nbsp;&nbsp;황&nbsp;&nbsp;표
    </h1>
    <div style="display: flex; flex-direction: column; align-items: center; position: relative;">
"""

for r_idx, row in enumerate(layout_rows):
    z_index = "2" if row["type"] == "circle" else "1"
    margin_top = "-50px" if r_idx > 0 and row["type"] == "circle" else ("-50px" if r_idx > 0 else "0px")
    
    html_drawing += f'<div style="display: flex; justify-content: center; margin-top: {margin_top}; z-index: {z_index};">'
    for name in row["names"]:
        if row["type"] == "circle":
            html_drawing += f'<div style="width: 90px; height: 90px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">{get_content(name)}</div>'
        else:
            html_drawing += f'<div style="width: 105px; height: 150px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: -2px;">{get_content(name)}</div>'
    html_drawing += '</div>'

html_drawing += "</div></div>"

# 최종 결과물 렌더링
st.markdown(html_drawing, unsafe_allow_html=True)
