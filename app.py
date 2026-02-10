import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json

# 1. 페이지 설정
st.set_page_config(layout="wide")

# 한국 시간 설정 함수
def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# --- 데이터 유지 로직 (파일 저장 방식) ---
# 웹을 껐다 켜도 데이터를 유지하기 위해 파일을 사용합니다.
DB_FILE = "inventory_db.json"

def save_data(data, last_time):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"data": data, "time": last_time}, f, ensure_ascii=False)

def load_data():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"data": {}, "time": "업데이트 기록 없음"}

# 초기 데이터 로드
saved_state = load_data()
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = saved_state["data"]
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = saved_state["time"]

# --- [상단] 데이터 입력 섹션 (중앙 정렬) ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=150, help="엑셀에서 '장치장 곡종 재고량' 영역을 복사해서 붙여넣으세요.")

# --- [중단] 업데이트 버튼 및 시간 (완벽 중앙 정렬) ---
st.markdown("<br>", unsafe_allow_html=True)
_, col_btn, _ = st.columns([1.2, 1, 1.2]) # 버튼 너비를 적절히 조절하여 중앙 배치

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
                # 콤마나 탭 등으로 구분된 데이터 처리 (데이터 형식 에러 방지)
                lines = raw_data.strip().split('\n')
                new_inventory = {}
                for line in lines:
                    parts = line.replace('\t', ' ').split() # 탭을 공백으로 변환 후 분리
                    if len(parts) >= 3:
                        name = parts[0]
                        crop = parts[1]
                        # 수량에서 콤마 제거 후 숫자로 변환
                        qty = int(float(parts[2].replace(',', '')))
                        new_inventory[name] = {"곡종": crop, "재고량": qty}
                
                st.session_state.inventory_data = new_inventory
                st.session_state.last_updated = get_seoul_time()
                # 파일에 저장 (껐다 켜도 유지)
                save_data(new_inventory, st.session_state.last_updated)
                st.rerun() 
            except Exception as e:
                st.error(f"데이터 형식 에러: {e}. '장치장 곡종 수량' 순서인지 확인해주세요.")
        else:
            st.warning("데이터를 입력해주세요.")
    
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 10px;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 ---
st.markdown("<br>", unsafe_allow_html=True)

# 총 재고수량 계산
total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())

def get_content(name):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    item = data.get("곡종", "-")
    qty = data.get("재고량", 0)
    qty_formatted = "{:,}".format(qty)
    return f'<div style="color: blue; font-weight: bold; font-size: 13px;">{item}</div><div style="color: black; font-weight: bold; font-size: 15px;">{qty_formatted}</div><div style="color: green; font-size: 11px;">{name}</div>'

# 회색 박스 시작
html_drawing = f"""
<div style="background-color: #f0f0f0; border: 1px solid #ccc; padding: 30px; border-radius: 10px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 0 20px;">
        <div style="width: 200px;"></div> <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin: 0;">일&nbsp;&nbsp;일&nbsp;&nbsp;재&nbsp;&nbsp;고&nbsp;&nbsp;현&nbsp;&nbsp;황&nbsp;&nbsp;표</h2>
        <div style="width: 200px; background: white; padding: 10px; border: 2px solid #333; text-align: center; font-weight: bold;">
            총 재고수량: <span style="color: red;">{total_stock:,}</span>
        </div>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center; position: relative; gap: 0px;">
"""

# 도면 배치 정의
layout_rows = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)]},
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)]},
    {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)]},
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)]}
]

for r_idx, row in enumerate(layout_rows):
    if row["type"] == "circle":
        # 동그라미 행: 사각형 사이사이에 오도록 마진 조절
        html_drawing += '<div style="display: flex; justify-content: center; margin: -50px 0; z-index: 2; gap: 20px;">'
        for name in row["names"]:
            html_drawing += f'<div style="width: 90px; height: 90px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">{get_content(name)}</div>'
    else:
        # 사각형 행: 딱 붙게 배치
        html_drawing += '<div style="display: flex; justify-content: center; margin: 0; z-index: 1;">'
        for name in row["names"]:
            html_drawing += f'<div style="width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-left: -2px;">{get_content(name)}</div>'
    html_drawing += '</div>'

html_drawing += "</div></div>"

# 최종 출력
st.markdown(html_drawing, unsafe_allow_html=True)

# 2. 필요한 라이브러리 설치 안내 (requirements.txt 수정용)
# pytz 가 필요하므로 requirements.txt에 추가해야 합니다.
