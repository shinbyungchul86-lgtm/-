import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide")

# 한국 시간 설정
def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# 데이터 유지 로직
DB_FILE = "inventory_db.json"

def save_data(data, last_time):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"data": data, "time": last_time}, f, ensure_ascii=False)

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"data": {}, "time": "업데이트 기록 없음"}
    return {"data": {}, "time": "업데이트 기록 없음"}

saved_state = load_data()
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = saved_state["data"]
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = saved_state["time"]

# --- [상단] 데이터 입력 섹션 ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=150, label_visibility="collapsed")

# --- [중단] 업데이트 버튼 및 시간 (위치 정밀 조정) ---
st.markdown("<br>", unsafe_allow_html=True)
# 버튼을 더 오른쪽으로 밀기 위해 컬럼 비율 조정 (세 번째 컬럼 너비 상향)
_, _, col_btn, col_time, _ = st.columns([1.5, 0.5, 1.2, 1.3, 1.0]) 

with col_btn:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            border-radius: 15px;
            font-weight: bold;
            width: 100%;
            height: 50px;
            font-size: 18px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("현황표 업데이트"):
        if raw_data.strip():
            try:
                lines = raw_data.strip().split('\n')
                new_inventory = {}
                for line in lines:
                    parts = line.replace('\t', ' ').split()
                    if len(parts) >= 3:
                        try:
                            val = parts[2].replace(',', '')
                            qty = int(float(val))
                            new_inventory[parts[0]] = {"곡종": parts[1], "재고량": qty}
                        except ValueError: continue
                st.session_state.inventory_data = new_inventory
                st.session_state.last_updated = get_seoul_time()
                save_data(new_inventory, st.session_state.last_updated)
                st.rerun() 
            except: st.error("데이터 처리 오류")

with col_time:
    # 시간을 조금 더 왼쪽으로 붙이기 위해 정렬과 마진 조정
    st.markdown(f"<div style='text-align: left; font-weight: bold; margin-top: 15px; font-size: 14px; white-space: nowrap;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 ---
st.markdown("<br>", unsafe_allow_html=True)

total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())

def get_item_html(name, qty_color="black", is_rect=False):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    qty_f = "{:,}".format(data.get("재고량", 0))
    
    # 사각형일 경우 곡종 색상을 짙은 감색(#000050)으로 설정
    crop_color = "#000050" if is_rect else "blue"
    # 장치장(이름) 색상을 짙은 회색(#555555)으로 설정
    name_color = "#555555"
    
    return f"""<div style="color: {crop_color}; font-weight: bold; font-size: 12px;">{data['곡종']}</div>
               <div style="color: {qty_color}; font-weight: bold; font-size: 14px;">{qty_f}</div>
               <div style="color: {name_color}; font-size: 11px;">{name}</div>"""

# 도면 구조 정의
rows_data = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)], "color": "#000080"}, # 감색
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)], "color": "#4b4b4b"}, # 짙은 회색
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)]}
]

# 전체 HTML 결합
# 자간(letter-spacing) 2배 확대 및 하단 박스 여백 조정
main_html = f"""
<div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 30px 20px 100px 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; font-family: sans-serif;">
    <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin: 0 0 25px 0; font-size: 28px; letter-spacing: 0.5em;">일 일 재 고 현 황 표</h2>
    
    <div style="width: 250px; background: white; padding: 8px; border: 1px solid #333; text-align: center; font-size: 15px; font-weight: bold; margin-bottom: 45px; white-space: nowrap;">
        총 재고수량: <span style="color: red;">{total_stock:,}</span>
    </div>
    
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
"""

for r_idx, row in enumerate(rows_data):
    is_circle = row["type"] == "circle"
    margin = "-44px 0" if is_circle and r_idx > 0 else ("0 0 -44px 0" if is_circle else "0")
    z_index = "2" if is_circle else "1"
    gap = "22px" if is_circle else "0"
    
    main_html += f'<div style="display: flex; justify-content: center; margin: {margin}; z-index: {z_index}; gap: {gap};">'
    for name in row["names"]:
        if is_circle:
            main_html += f'<div style="width: 88px; height: 88px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.15);">{get_item_html(name)}</div>'
        else:
            main_html += f'<div style="width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: -2px;">{get_item_html(name, row.get("color", "black"), is_rect=True)}</div>'
    main_html += '</div>'

main_html += "</div></div>"

st.markdown(main_html, unsafe_allow_html=True)
