import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; text-decoration: underline;'>일&nbsp;&nbsp;일&nbsp;&nbsp;재&nbsp;&nbsp;고&nbsp;&nbsp;현&nbsp;&nbsp;황&nbsp;&nbsp;표</h1>", unsafe_allow_html=True)

# --- 상단: 데이터 입력 섹션 ---
st.subheader("데이터 입력 (엑셀 복사/붙여넣기)")
raw_data = st.text_area("엑셀의 '장치장, 곡종, 재고량' 데이터를 복사해 붙여넣으세요.", height=150, placeholder="예: A101  옥수수  1,500")

# --- 데이터 저장소 설정 (상태 유지) ---
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = {}
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = "업데이트 기록 없음"

# --- 중단: 업데이트 버튼 섹션 ---
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            width: 180px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("현황표 업데이트"):
        if raw_data:
            try:
                # 데이터를 줄 단위로 나누고 처리
                lines = [line.split() for line in raw_data.strip().split('\n')]
                # 데이터가 있는 줄만 필터링하여 데이터프레임 생성
                valid_lines = [l for l in lines if len(l) >= 3]
                df = pd.DataFrame(valid_lines).iloc[:, :3]
                df.columns = ['장치장', '곡종', '재고량']
                st.session_state.inventory_data = df.set_index('장치장').to_dict('index')
                
                now = datetime.now()
                st.session_state.last_updated = now.strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")
                st.rerun() 
            except Exception as e:
                st.error("데이터 형식을 확인해주세요. (장치장 곡종 재고량 순서)")
        else:
            st.warning("데이터를 입력해주세요.")

with col2:
    st.markdown(f"<br><b>{st.session_state.last_updated}</b>", unsafe_allow_html=True)

# --- 하단: 창고 도식화 섹션 ---
st.divider()

def draw_storage(name):
    # 데이터 매칭 (없으면 기본값)
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": "0"})
    item = data.get("곡종", "-")
    qty = str(data.get("재고량", "0"))
    
    # 천단위 컴마 처리
    try:
        clean_qty = qty.replace(',', '')
        qty_formatted = "{:,}".format(int(clean_qty))
    except:
        qty_formatted = qty

    return f"""
    <div style="text-align: center; line-height: 1.3;">
        <div style="color: blue; font-weight: bold; font-size: 14px; margin-bottom: 2px;">{item}</div>
        <div style="color: black; font-weight: bold; font-size: 16px; margin-bottom: 2px;">{qty_formatted}</div>
        <div style="color: green; font-size: 12px;">{name}</div>
    </div>
    """

# --- 요청하신 창고 이름 규칙 정의 ---
layout_rows = [
    {"type": "circle", "names": [f"A10{i}" for i in range(1, 7)]}, # 1행: A101~A106
    {"type": "rect",   "names": [f"A20{i}" for i in range(1, 8)]}, # 2행: A201~A207
    {"type": "circle", "names": [f"A30{i}" for i in range(1, 7)]}, # 3행: A301~A306
    {"type": "rect",   "names": [f"A40{i}" for i in range(1, 8)]}, # 4행: A401~A407
    {"type": "circle", "names": [f"A50{i}" for i in range(1, 7)]}  # 5행: A501~A506
]

# 화면에 도면 그리기
for row in layout_rows:
    cols = st.columns(7) # 7열 기준 레이아웃
    for idx, name in enumerate(row["names"]):
        with cols[idx]:
            shape_style = "border-radius: 50%;" if row["type"] == "circle" else "border-radius: 8px;"
            st.markdown(f"""
                <div style="border: 2px solid #333; {shape_style} 
                height: 105px; width: 105px; display: flex; align-items: center; justify-content: center; 
                background-color: #ffffff; margin: 10px auto; box-shadow: 3px 3px 8px rgba(0,0,0,0.1);">
                    {draw_storage(name)}
                </div>
            """, unsafe_allow_html=True)
