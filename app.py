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

# --- [중단] 업데이트 버튼 및 시간 ---
st.markdown("<br>", unsafe_allow_html=True)
_, col_center, _ = st.columns([0.8, 1.4, 0.8])

with col_center:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            border-radius: 15px;
            font-weight: bold;
            width: 100%;
            height: 65px;
            font-size: 20px;
            border: 2px solid #1e7e34;
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
    
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 8px; font-size: 16px;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 데이터 계산 ---
rect_rows = [
    [f"A20{i}" for i in range(1, 8)], # 사각형 1행
    [f"A40{i}" for i in range(1, 8)]  # 사각형 2행
]
circle_rows = [
    [f"A10{i}" for i in range(1, 7)], # 동그라미 1행 (사각형 사이)
    [f"A30{i}" for i in range(1, 7)], # 동그라미 2행 (사각형 사이)
    [f"A50{i}" for i in range(1, 7)]  # 동그라미 3행 (사각형 사이)
]

total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())
rect_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in rect_rows for n in row)
circle_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in circle_rows for n in row)

def get_item_html(name, is_rect=False):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    qty_f = "{:,}".format(data.get("재고량", 0))
    name_color = "#555555"
    if is_rect:
        crop_color = "#FF8C00"; qty_color = "black"
    else:
        crop_color = "blue"; qty_color = "black"
    return f'<div style="color: {crop_color}; font-weight: bold; font-size: 12px; line-height:1.2;">{data["곡종"]}</div>' \
           f'<div style="color: {qty_color}; font-weight: bold; font-size: 14px; line-height:1.2;">{qty_f}</div>' \
           f'<div style="color: {name_color}; font-size: 11px; line-height:1.2;">{name}</div>'

# ---------------------------------------------------------
# 도면 렌더링 로직 (Absolute Layering 방식)
# ---------------------------------------------------------
RECT_W = 110
RECT_H = 160
CIRC_D = 88

final_html = f"""
<div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 40px 20px 80px 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin: 0 0 25px 0; font-size: 28px; letter-spacing: 0.25em;">일 일 재 고 현 황 표</h2>
    <div style="min-width: 750px; background: white; padding: 15px 30px; border: 1px solid #333; text-align: center; font-size: 16px; font-weight: bold; margin-bottom: 50px; white-space: nowrap; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
        총 재고수량 : <span style="color: red;">{total_stock:,}개</span> / 
        사각형 재고수량 : <span style="color: blue;">{rect_sum:,}개</span> / 
        동그라미 재고수량 : <span style="color: #FF8C00;">{circle_sum:,}개</span>
    </div>

    <div style="position: relative; width: {RECT_W * 7}px; height: 500px; margin-top: 40px;">
"""

# 1. 사각형 배치 (A201~A207, A401~A407)
for r_idx, row in enumerate(rect_rows):
    y_pos = r_idx * (RECT_H + 80) # 사각형 행 간 간격
    for c_idx, name in enumerate(row):
        x_pos = c_idx * (RECT_W - 2) # 테두리 겹침 보정
        final_html += f'''
        <div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: {RECT_W}px; height: {RECT_H}px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1;">
            {get_item_html(name, is_rect=True)}
        </div>'''

# 2. 동그라미 배치 (사각형 사이 경계선 정중앙)
# 동그라미 행 위치 정의: 사각형 상단, 사각형 사이, 사각형 하단
y_offsets = [-CIRC_D/2, RECT_H - CIRC_D/2, (RECT_H + 80) + RECT_H - CIRC_D/2]

for r_idx, row in enumerate(circle_rows):
    y_pos = y_offsets[r_idx]
    for c_idx, name in enumerate(row):
        # 사각형 사이의 경계선 위치 = (현재 사각형의 끝 지점)
        x_pos = (c_idx + 1) * RECT_W - (CIRC_D / 2) - (c_idx * 2)
        final_html += f'''
        <div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: {CIRC_D}px; height: {CIRC_D}px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            {get_item_html(name, is_rect=False)}
        </div>'''

final_html += "</div></div>"

st.markdown(final_html, unsafe_allow_html=True)
