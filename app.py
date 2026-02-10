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
rect_names = [f"A20{i}" for i in range(1, 8)] + [f"A40{i}" for i in range(1, 8)]
circle_names = [f"A10{i}" for i in range(1, 7)] + [f"A30{i}" for i in range(1, 7)] + [f"A50{i}" for i in range(1, 7)]

total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())
rect_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for n in rect_names)
circle_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for n in circle_names)

def get_item_html(name, is_rect=False):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    qty_f = "{:,}".format(data.get("재고량", 0))
    name_color = "#555555"
    
    if is_rect:
        crop_color = "#FF8C00" # 짙은 주황색
        qty_color = "black"
    else:
        crop_color = "blue"
        qty_color = "black"
    
    return f'<div style="color: {crop_color}; font-weight: bold; font-size: 12px;">{data["곡종"]}</div>' \
           f'<div style="color: {qty_color}; font-weight: bold; font-size: 14px;">{qty_f}</div>' \
           f'<div style="color: {name_color}; font-size: 11px;">{name}</div>'

# 도면 구조 정의
rows_data = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)]},
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)]},
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)]}
]

# 전체 HTML 생성
final_html = f"""
<div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 40px 20px 100px 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin: 0 0 25px 0; font-size: 28px; letter-spacing: 0.25em;">일 일 재 고 현 황 표</h2>
    <div style="min-width: 750px; background: white; padding: 15px 30px; border: 1px solid #333; text-align: center; font-size: 16px; font-weight: bold; margin-bottom: 50px; white-space: nowrap; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
        총 재고수량 : <span style="color: red;">{total_stock:,}개</span> / 
        사각형 재고수량 : <span style="color: blue;">{rect_sum:,}개</span> / 
        동그라미 재고수량 : <span style="color: #FF8C00;">{circle_sum:,}개</span>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center;">
"""

for r_idx, row in enumerate(rows_data):
    is_c = row["type"] == "circle"
    row_margin = "-44px 0" if is_c and r_idx > 0 else ("0 0 -44px 0" if is_c else "0")
    
    final_html += f'<div style="display: flex; justify-content: center; margin: {row_margin}; z-index: {"2" if is_c else "1"};">'
    for i, name in enumerate(row["names"]):
        if is_c:
            # 동그라미 위치 미세 조정 (margin-left/right를 통해 좌우에서 안쪽으로 밀어줌)
            circle_style = "width: 88px; height: 88px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin: 0 11px;"
            if i == 0: circle_style += " margin-left: 30px;" # 첫번째 동그라미 오른쪽으로
            if i == 1: circle_style += " margin-left: 30px;" # 두번째 동그라미 오른쪽으로
            if i == 2: circle_style += " margin-left: 20px;" # 두번째 동그라미 오른쪽으로
            if i == 3: circle_style += " margin-right: 20px;" # 다섯번째 동그라미 왼쪽으로
            if i == 4: circle_style += " margin-right: 30px;" # 다섯번째 동그라미 왼쪽으로
            if i == 5: circle_style += " margin-right: 30px;" # 마지막 동그라미 왼쪽으로
            
            final_html += f'<div style="{circle_style}">{get_item_html(name, is_rect=False)}</div>'
        else:
            final_html += f'<div style="width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: -2px;">{get_item_html(name, is_rect=True)}</div>'
    final_html += '</div>'

final_html += "</div></div>"

st.markdown(final_html, unsafe_allow_html=True)
