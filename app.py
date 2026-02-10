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

# 데이터 로직 생략 (기존과 동일)
# ... [이전 답변의 save_data, load_data 로직 유지] ...

# --- [상단] 데이터 입력 섹션 ---
st.markdown("<h3 style='text-align: center;'>데이터 입력 (엑셀 복사/붙여넣기)</h3>", unsafe_allow_html=True)
raw_data = st.text_area("", height=60, label_visibility="collapsed")

# --- [중단] 커스텀 업데이트 버튼 (우측 끝 배치 및 투톤 색상) ---
# 컬럼 비율을 [2, 0.5, 1.5]로 설정하여 버튼을 오른쪽으로 더 밀어냅니다.
col_empty, col_btn = st.columns([2.5, 1.5])

with col_btn:
    # CSS를 이용한 버튼 투톤 디자인 및 텍스트 설정
    st.markdown(f"""
        <style>
        /* Streamlit 기본 버튼 숨기기 및 커스텀 스타일링 */
        div.stButton > button:first-child {{
            width: 100%;
            height: 90px;
            padding: 0;
            border: 2px solid #333;
            border-radius: 10px;
            overflow: hidden;
            background: none;
            display: flex;
            flex-direction: column;
        }}
        
        .btn-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .btn-top {{
            background-color: #28a745; /* 상단 초록색 */
            color: black;              /* 검은색 글자 */
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 19px;
            font-weight: bold;
        }}
        
        .btn-bottom {{
            background-color: #000000; /* 하단 검은색 */
            color: white;              /* 흰색 글자 */
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 버튼 내부 구성을 HTML로 미리 정의 (상단: 고정텍스트, 하단: 시간)
    button_inner_html = f"""
        <div class="btn-container">
            <div class="btn-top">현황표 업데이트</div>
            <div class="btn-bottom">{st.session_state.last_updated}</div>
        </div>
    """
    
    # 실제 Streamlit 버튼 (투명하게 덮어쓰기 위해 라벨은 공백으로 두거나 CSS로 가림)
    if st.button("현황표 업데이트 버튼", use_container_width=True):
        if raw_data.strip():
            try:
                lines = raw_data.strip().split('\n')
                new_inventory = {}
                for line in lines:
                    parts = line.replace('\t', ' ').split()
                    if len(parts) >= 3:
                        qty = int(float(parts[2].replace(',', '')))
                        new_inventory[parts[0]] = {"곡종": parts[1], "재고량": qty}
                st.session_state.inventory_data = new_inventory
                st.session_state.last_updated = get_seoul_time()
                # save_data(new_inventory, st.session_state.last_updated) # 저장 로직 필요 시 주석 해제
                st.rerun()
            except: st.error("데이터 형식 오류")

    # 버튼 위에 HTML 텍스트를 덧씌우는 트릭 (Streamlit 버튼 위에 레이어 올리기)
    st.markdown(f"""
        <script>
            var buttons = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.includes("현황표 업데이트 버튼")) {{
                    buttons[i].innerHTML = `{button_inner_html}`;
                }}
            }}
        </script>
    """, unsafe_allow_html=True)

# --- [하단] 도식화 레이아웃 (기존 로직 동일) ---
# ... [이전 답변의 final_html 생성 로직 유지] ...
