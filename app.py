import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(layout="wide")

# --- [상단] 데이터 입력 섹션 ---
st.subheader("데이터 입력 (엑셀 복사/붙여넣기)")
raw_data = st.text_area("엑셀의 '장치장, 곡종, 재고량' 데이터를 붙여넣으세요.", height=150, placeholder="예: A101  옥수수  1500")

# --- 데이터 저장소 설정 ---
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

# --- [중단] 업데이트 버튼 및 시간 (중앙 정렬) ---
st.markdown("<br>", unsafe_allow_html=True)
col_left, col_mid, col_right = st.columns([1, 1, 1])

with col_mid:
    # 버튼 스타일: 초록색, 둥근 모서리
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
        if raw_data:
            try:
                lines = [line.split() for line in raw_data.strip().split('\n')]
                valid_lines = [l for l in lines if len(l) >= 3]
                df = pd.DataFrame(valid_lines).iloc[:, :3]
                df.columns = ['장치장', '곡종', '재고량']
                st.session_state.inventory_data = df.set_index('장치장').to_dict('index')
                now = datetime.now()
                st.session_state.last_updated = now.strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")
                st.rerun() 
            except:
                st.error("데이터 형식을 확인해주세요.")
    
    # 버튼 아래 업데이트 시간 표시
    st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 10px;'>{st.session_state.last_updated}</div>", unsafe_allow_html=True)

# --- [하단] 재고현황표 도식화 (옅은 회색 박스 내부) ---
st.markdown("<br>", unsafe_allow_html=True)

# 옅은 회색 배경 박스 시작
st.markdown("""
    <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 40px 20px;">
        <h1 style="text-align: center; text-decoration: underline; font-weight: bold; margin-bottom: 50px;">
            일&nbsp;&nbsp;일&nbsp;&nbsp;재&nbsp;&nbsp;고&nbsp;&nbsp;현&nbsp;&nbsp;황&nbsp;&nbsp;표
        </h1>
""", unsafe_allow_html=True)

def get_html_content(name):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": "0"})
    item = data.get("곡종", "-")
    qty = str(data.get("재고량", "0"))
    try:
        # 소수점 제거 및 정수 처리
        qty_int = int(float(qty.replace(',', '')))
        qty_formatted = "{:,}".format(qty_int)
    except:
        qty_formatted = "0"
    
    return f"""
        <div style="color: blue; font-weight: bold; font-size: 13px;">{item}</div>
        <div style="color: black; font-weight: bold; font-size: 15px;">{qty_formatted}</div>
        <div style="color: green; font-size: 11px;">{name}</div>
    """

# 창고 레이아웃 배치 (CSS Grid 활용)
# 사각형은 딱 붙고, 동그라미는 그 사이 교차점에 위치하게 조정
storage_html = '<div style="display: flex; flex-direction: column; align-items: center; position: relative;">'

# 행 데이터 정의
rows = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)], "margin": "0 0 -40px 0", "z": "2"},
    {"type": "rect", "names": [f"A20{i}" for i in range(1, 8)], "margin": "0", "z": "1"},
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)], "margin": "-40px 0 -40px 0", "z": "2"},
    {"type": "rect", "names": [f"A40{i}" for i in range(1, 8)], "margin": "0", "z": "1"},
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)], "margin": "-40px 0 0 0", "z": "2"}
]

for row in rows:
    style = f"display: flex; justify-content: center; margin: {row['margin']}; z-index: {row['z']};"
    storage_html += f'<div style="{style}">'
    for name in row["names"]:
        if row["type"] == "circle":
            # 동그라미 디자인
            storage_html += f"""
                <div style="width: 90px; height: 90px; border: 2px solid #333; border-radius: 50%; 
                background: white; display: flex; flex-direction: column; align-items: center; 
                justify-content: center; margin: 0 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                    {get_html_content(name)}
                </div>"""
        else:
            # 사각형 디자인 (직각, 세로 1.5배 확장, 테두리 공유를 위해 마이너스 마진)
            storage_html += f"""
                <div style="width: 100px; height: 140px; border: 2px solid #333; 
                background: #fff; display: flex; flex-direction: column; align-items: center; 
                justify-content: center; margin-left: -2px;">
                    {get_html_content(name)}
                </div>"""
    storage_html += "</div>"

storage_html += "</div>"
st.markdown(storage_html, unsafe_allow_html=True)

# 회색 박스 닫기
st.markdown("</div>", unsafe_allow_html=True)
