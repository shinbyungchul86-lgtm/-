import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide")

# 2. 세션 상태 초기화
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# --- [상단] 데이터 입력 섹션 ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=60, label_visibility="collapsed", key="data_input")

# --- [중단] 커스텀 투톤 버튼 및 위치 조정 ---
# 1:2.5 비율로 나누어 버튼을 최대한 오른쪽 끝으로 밀어냅니다.
_, col_btn = st.columns([1, 2.5])

with col_btn:
    # CSS: 버튼 내부를 초록/검정으로 정확히 쪼개고 텍스트 색상 개별 적용
    st.markdown(f"""
        <style>
        div.stButton > button:first-child {{
            width: 320px; /* 버튼 크기 고정 */
            height: 90px;
            float: right; /* 버튼 자체를 우측 정렬 */
            padding: 0 !important;
            border: 2px solid #333 !important;
            border-radius: 12px !important;
            background: linear-gradient(to bottom, #28a745 50%, #000000 50%) !important;
            color: transparent !important; /* 기본 라벨 숨김 */
            position: relative;
            overflow: hidden;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
        }}
        
        /* 상단: 초록색 배경 위 검은색 텍스트 */
        div.stButton > button:first-child::before {{
            content: "현황표 업데이트";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 50%;
            display: flex; align-items: center; justify-content: center;
            color: black !important;
            font-size: 18px !important;
            font-weight: bold !important;
        }}
        
        /* 하단: 검은색 배경 위 흰색 텍스트 */
        div.stButton > button:first-child::after {{
            content: "{st.session_state.last_updated}";
            position: absolute;
            bottom: 0; left: 0; width: 100%; height: 50%;
            display: flex; align-items: center; justify-content: center;
            color: white !important;
            font-size: 13px !important;
            font-weight: normal !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    if st.button("Update_Trigger"): # 실제 작동을 위한 트리거
        if raw_data.strip():
            lines = raw_data.strip().split('\n')
            new_inv = {}
            for line in lines:
                parts = line.replace('\t', ' ').split()
                if len(parts) >= 3:
                    try:
                        qty = int(float(parts[2].replace(',', '')))
                        new_inv[parts[0]] = {"곡종": parts[1], "재고량": qty}
                    except: continue
            st.session_state.inventory_data = new_inv
            st.session_state.last_updated = get_seoul_time()
            st.rerun()

# --- [하단] 도식화 레이아웃 로직 (사각형 밀착 버전) ---
# ... (이후 렌더링 코드는 이전과 동일하게 유지)
