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

# --- [상단] 데이터 입력 섹션 (중앙 정렬) ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=150, label_visibility="collapsed")

# --- [중단] 업데이트 버튼 (정중앙 배치) ---
st.markdown("<br>", unsafe_allow_html=True)
# 비율을 조절하여 버튼을 정중앙으로 배치
_, _, col_btn, _, _ = st.columns([1.5, 1, 1, 1, 1.5]) 

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
                        except ValueError:
                            continue
                
                st.session_state.inventory_data = new_inventory
                st.session_state.last_updated = get_seoul_time()
                save_data(new_inventory, st.session_state.last_updated)
                st.rerun() 
            except Exception as e:
                st.error("데이터 처리 중 오류가 발생했습니다.")
    
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 10px; font-size: 14px; white-space: nowrap;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 ---
st.markdown("<br>", unsafe_allow_html=True)

# 총 재고수량 계산
total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())

# HTML 렌더링 함수
def render_storage_map():
    def get_content(name):
        data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
        qty_formatted = "{:,}".format(data.get("재고량", 0))
        return f'<div style="color: blue; font-weight: bold; font-size: 11px;">{data["곡종"]}</div><div style="color: black; font-weight: bold; font-size: 13px;">{qty_formatted}</div><div style="color: green; font-size: 10px;">{name}</div>'

    rows = [
        {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)]},
        {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)]},
        {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)]},
        {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)]},
        {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)]}
    ]

    html = f"""
    <div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 30px; border-radius: 10px;">
        <h3 style="text-align: center; text-decoration: underline; font-weight: bold; margin-top: 0; margin-bottom: 20px;">일 일 재 고 현 황 표</h3>
        <div style="display: flex; justify-content: center; margin-bottom: 30px;">
            <div style="width: 150px; background: white; padding: 5px; border: 1px solid #333; text-align: center; font-size: 13px; font-weight: bold;">
                총 재고수량: <span style="color: red;">{total_stock:,}</span>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center;">
    """

    for r_idx, row in enumerate(rows):
        is_circle = row["type"] == "circle"
        margin = "-45px 0" if is_circle and r_idx > 0 else ("0" if not is_circle else "0 0 -45px 0")
        z_index = "2" if is_circle else "1"
        gap = "28px" if is_circle else "0"
        
        html += f'<div style="display: flex; justify-content: center; margin: {margin}; z-index: {z_index}; gap: {gap};">'
        for name in row["names"]:
            if is_circle:
                html += f'<div style="width: 85px; height: 85px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">{get_content(name)}</div>'
            else:
                html += f'<div style="width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: -2px;">{get_content(name)}</div>'
        html += '</div>'

    html += "</div></div>"
    return html

st.markdown(render_storage_map(), unsafe_allow_html=True)
