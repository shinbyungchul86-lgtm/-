import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os

# 1. 페이지 설정 (가장 먼저 실행되어야 함)
st.set_page_config(layout="wide")

# 2. 세션 상태 초기화 (AttributeError 방지 핵심 로직)
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

# 한국 시간 설정 함수
def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# 데이터 유지/로드 로직 (DB_FILE 연동)
DB_FILE = "inventory_db.json"

def save_data(data, last_time):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"data": data, "time": last_time}, f, ensure_ascii=False)

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                return content.get("data", {}), content.get("time", "업데이트 기록 없음")
        except:
            return {}, "업데이트 기록 없음"
    return {}, "업데이트 기록 없음"

# 앱 시작 시 파일에서 데이터 불러오기 (한 번만 실행)
if not st.session_state.inventory_data or st.session_state.last_updated == "업데이트 기록 없음":
    data, time = load_data()
    st.session_state.inventory_data = data
    st.session_state.last_updated = time

# --- [상단] 데이터 입력 섹션 ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=100, label_visibility="collapsed")

# --- [중단] 업데이트 버튼 및 시간 ---
_, col_center, _ = st.columns([0.8, 1.4, 0.8])
with col_center:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #28a745; color: white; border-radius: 15px;
            font-weight: bold; width: 100%; height: 65px; font-size: 20px; border: 2px solid #1e7e34;
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
            except: st.error("데이터 형식 오류")
    
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 8px; font-size: 16px;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 도식화 레이아웃 로직 ---
rect_rows = [[f"A20{i}" for i in range(1, 8)], [f"A40{i}" for i in range(1, 8)]]
circle_rows = [[f"A10{i}" for i in range(1, 7)], [f"A30{i}" for i in range(1, 7)], [f"A50{i}" for i in range(1, 7)]]

# 안전한 합계 계산 (데이터가 없을 경우 0 처리)
total_stock = sum(int(info.get("재고량", 0)) for info in st.session_state.inventory_data.values())
rect_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in rect_rows for n in row)
circle_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in circle_rows for n in row)

def get_item_html(name, is_rect=False):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    qty_f = "{:,}".format(data.get("재고량", 0))
    crop_color = "#FF8C00" if is_rect else "blue"
    return f'<div style="color: {crop_color}; font-weight: bold; font-size: 12px; line-height:1.1;">{data["곡종"]}</div>' \
           f'<div style="color: black; font-weight: bold; font-size: 14px; line-height:1.1;">{qty_f}</div>' \
           f'<div style="color: #555555; font-size: 11px; line-height:1.1;">{name}</div>'

# HTML 렌더링 (Absolute Positioning)
final_html = f"""
<div style="background-color: #eeeeee; padding: 40px 20px 100px 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin-bottom: 25px; font-size: 28px; letter-spacing: 0.25em;">일 일 재 고 현 황 표</h2>
    <div style="min-width: 750px; background: white; padding: 15px 30px; border: 1px solid #333; text-align: center; font-size: 16px; font-weight: bold; margin-bottom: 50px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
        총 재고수량 : <span style="color: red;">{total_stock:,}개</span> / 
        사각형 재고수량 : <span style="color: blue;">{rect_sum:,}개</span> / 
        동그라미 재고수량 : <span style="color: #FF8C00;">{circle_sum:,}개</span>
    </div>
    <div style="position: relative; width: 758px; height: 500px; margin-top: 50px;">
"""

# 사각형 렌더링
for r_idx, row in enumerate(rect_rows):
    for c_idx, name in enumerate(row):
        final_html += f'<div style="position: absolute; left: {c_idx * 108}px; top: {r_idx * 240}px; width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1;">{get_item_html(name, True)}</div>'

# 동그라미 렌더링 (사각형 경계선 정중앙 정렬)
y_offsets = [-44, 116, 356]
for r_idx, row in enumerate(circle_rows):
    for c_idx, name in enumerate(row):
        final_html += f'<div style="position: absolute; left: {(c_idx + 1) * 108 - 44}px; top: {y_offsets[r_idx]}px; width: 88px; height: 88px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">{get_item_html(name, False)}</div>'

final_html += "</div></div>"
st.markdown(final_html, unsafe_allow_html=True)
