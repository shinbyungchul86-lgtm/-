import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

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
raw_data = st.text_area("", height=60, label_visibility="collapsed")

# --- [중단] 버튼 투톤 색상 및 우측 정렬 (강력 보정 버전) ---
# 왼쪽 빈 공간(4) : 버튼 공간(1) 비율로 버튼을 오른쪽 끝으로 배치
_, col_btn = st.columns([4, 1])

with col_btn:
    st.markdown(f"""
        <style>
        /* 버튼 본체 스타일 - 상하 색상 강제 분리 */
        div.stButton > button {{
            width: 100% !important;
            height: 100px !important;
            padding: 0 !important;
            border: 2px solid #333 !important;
            border-radius: 10px !important;
            /* 위 50%는 초록, 아래 50%는 검정 (경계선 선명하게) */
            background: linear-gradient(to bottom, #28a745 0%, #28a745 50%, #000000 50%, #000000 100%) !important;
            color: transparent !important; /* 기본 흰색 텍스트 제거 */
            position: relative !important;
            overflow: hidden !important;
            display: block !important;
        }}

        /* 상단 텍스트 레이어: 현황표 업데이트 (검은색 글자) */
        div.stButton > button::before {{
            content: "현황표 업데이트" !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #000000 !important;
            font-size: 18px !important;
            font-weight: bold !important;
            z-index: 10 !important;
        }}

        /* 하단 텍스트 레이어: 시간 (흰색 글자) */
        div.stButton > button::after {{
            content: "{st.session_state.last_updated}" !important;
            position: absolute !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #ffffff !important;
            font-size: 13px !important;
            font-weight: normal !important;
            z-index: 10 !important;
        }}
        
        /* 버튼 클릭 시 발생하는 기본 효과 제거 (색상 유지) */
        div.stButton > button:active, div.stButton > button:focus, div.stButton > button:hover {{
            background: linear-gradient(to bottom, #28a745 0%, #28a745 50%, #000000 50%, #000000 100%) !important;
            border-color: #333 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    if st.button("현황표_업데이트_실행"):
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

# --- [하단] 도식화 레이아웃 (이전 답변 코드 유지) ---
# ... (생략된 현황표 렌더링 코드) ...
