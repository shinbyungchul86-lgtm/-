import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
import os

# 페이지 설정 및 기본 로직 (기존과 동일)
st.set_page_config(layout="wide")

def get_seoul_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime("%Y년 %m월 %d일 %H시 %M분 최종 업데이트")

# 데이터 로드/저장 로직 생략 (기존 코드 유지)
# ... [중환 생략: 이전 답변의 데이터 처리 부분 삽입] ...

# --- [하단] 재고현황표 도식화 데이터 계산 ---
rect_rows = [[f"A20{i}" for i in range(1, 8)], [f"A40{i}" for i in range(1, 8)]]
circle_rows = [[f"A10{i}" for i in range(1, 7)], [f"A30{i}" for i in range(1, 7)], [f"A50{i}" for i in range(1, 7)]]

# 재고 합계 계산
total_stock = sum(int(info["재고량"]) for info in st.session_state.inventory_data.values())
rect_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in rect_rows for n in row)
circle_sum = sum(int(st.session_state.inventory_data.get(n, {"재고량":0})["재고량"]) for row in circle_rows for n in row)

def get_item_html(name, is_rect=False):
    data = st.session_state.inventory_data.get(name, {"곡종": "-", "재고량": 0})
    qty_f = "{:,}".format(data.get("재고량", 0))
    if is_rect:
        crop_color = "#FF8C00"; qty_color = "black"
    else:
        crop_color = "blue"; qty_color = "black"
    return f'<div style="color: {crop_color}; font-weight: bold; font-size: 12px; line-height:1.1;">{data["곡종"]}</div>' \
           f'<div style="color: {qty_color}; font-weight: bold; font-size: 14px; line-height:1.1;">{qty_f}</div>' \
           f'<div style="color: #555555; font-size: 11px; line-height:1.1;">{name}</div>'

# ---------------------------------------------------------
# 정밀 좌표 렌더링 시작
# ---------------------------------------------------------
# 가로 기준점: 사각형 left가 108씩 증가하므로, 그 사이값은 108, 216, 324, 432, 540, 648
# 동그라미 지름 88px -> 반지름 44px
# ---------------------------------------------------------

final_html = f"""
<div style="background-color: #eeeeee; border: 1px solid #ccc; padding: 40px 20px 100px 20px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; font-family: 'Malgun Gothic', sans-serif;">
    <h2 style="text-align: center; text-decoration: underline; font-weight: bold; margin: 0 0 25px 0; font-size: 28px; letter-spacing: 0.25em;">일 일 재 고 현 황 표</h2>
    <div style="min-width: 750px; background: white; padding: 15px 30px; border: 1px solid #333; text-align: center; font-size: 16px; font-weight: bold; margin-bottom: 50px; white-space: nowrap; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
        총 재고수량 : <span style="color: red;">{total_stock:,}개</span> / 
        사각형 재고수량 : <span style="color: blue;">{rect_sum:,}개</span> / 
        동그라미 재고수량 : <span style="color: #FF8C00;">{circle_sum:,}개</span>
    </div>

    <div style="position: relative; width: 758px; height: 500px; margin-top: 50px;">
"""

# 1. 사각형 배치 (A20x, A40x)
for r_idx, row in enumerate(rect_rows):
    y_pos = r_idx * 240  # 사각형 행 사이 간격
    for c_idx, name in enumerate(row):
        x_pos = c_idx * 108 # 사각형 테두리 중첩 고려한 간격
        final_html += f'''
        <div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: 110px; height: 160px; border: 2px solid #333; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1;">
            {get_item_html(name, is_rect=True)}
        </div>'''

# 2. 동그라미 배치 (사각형 사이 수직 경계선에 정중앙 배치)
# y_offsets: 상단 라인(-44), 중앙 라인(120), 하단 라인(400-44=356)
y_offsets = [-44, 116, 356]

for r_idx, row in enumerate(circle_rows):
    y_pos = y_offsets[r_idx]
    for c_idx, name in enumerate(row):
        # 경계선 위치 (108, 216, 324...) - 반지름(44) = 중심 정렬
        x_pos = (c_idx + 1) * 108 - 44
        final_html += f'''
        <div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: 88px; height: 88px; border: 2px solid #333; border-radius: 50%; background: white; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 2; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            {get_item_html(name, is_rect=False)}
        </div>'''

final_html += "</div></div>"
st.markdown(final_html, unsafe_allow_html=True)
