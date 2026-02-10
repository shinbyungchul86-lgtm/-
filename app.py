import streamlit as st
from datetime import datetime
import pytz
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide")

# 2. 세션 상태 초기화 (AttributeError 방지)
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# --- [상단] 데이터 입력 섹션 ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=60, label_visibility="collapsed", key="input_area")

# --- [중단] 커스텀 투톤 버튼 (우측 배치) ---
# col 비율을 조정하여 버튼을 오른쪽으로 배치
_, col_btn = st.columns([3, 1]) 

with col_btn:
    # CSS를 이용해 버튼을 상/하단으로 쪼개는 효과 구현
    st.markdown(f"""
        <style>
        div.stButton > button:first-child {{
            width: 100%;
            height: 95px;
            padding: 0 !important;
            border: 2px solid #333 !important;
            border-radius: 12px !important;
            background: linear-gradient(to bottom, #28a745 50%, #000000 50%) !important;
            color: transparent !important; /* 기본 글자 숨김 */
            position: relative;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        }}
        /* 버튼 내 상단 텍스트 (초록색 영역) */
        div.stButton > button:first-child::before {{
            content: "현황표 업데이트";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            display: flex; align-items: center; justify-content: center;
            color: black; font-size: 18px; font-weight: bold;
        }}
        /* 버튼 내 하단 텍스트 (검은색 영역) */
        div.stButton > button:first-child::after {{
            content: "{st.session_state.last_updated}";
            position: absolute;
            bottom: 0; left: 0; width: 100%; height: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 13px; font-weight: normal;
        }}
        </style>
    """, unsafe_allow_html=True)

    if st.button("update_trigger"): # 라벨은 CSS로 가려지므로 내부 식별용
        if raw_data.strip():
            lines = raw_data.strip().split('\n')
            new_inventory = {}
            for line in lines:
                parts = line.replace('\t', ' ').split()
                if len(parts) >= 3:
                    try:
                        qty = int(float(parts[2].replace(',', '')))
                        new_inventory[parts[0]] = {"곡종": parts[1], "재고량": qty}
                    except: continue
            st.session_state.inventory_data = new_inventory
            st.session_state.last_updated = get_seoul_time()
            st.rerun()

# --- [하단] 도식화 레이아웃 (기존 로직 동일) ---
# ... (재고 현황표 렌더링 부분 생략) ...
