import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from PIL import Image

# --- [쑤샘영어: 파일 경로 및 구글 연결 설정] ---
# 프로그램이 있는 위치를 스스로 찾아서 열쇠(JSON)를 가져오도록 설정했습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(current_dir, "credentials.json")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # 경로를 자동 추적하여 credentials.json 파일을 읽습니다.
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
    client = gspread.authorize(creds)
    
    # 원장님이 주신 구글 시트 ID입니다.
    SHEET_ID = "1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE"
    sheet = client.open_by_key(SHEET_ID).sheet1
    connection_success = True
except Exception as e:
    connection_success = False
    error_msg = e

# 쑤샘영어 소중한 제자 명단 (31명)
STUDENT_LIST = [
    "권도해", "이재민", "송연주", "이다원", "송하준", "허민우", "이소미", 
    "경지윤", "정주안", "천준영", "하윤성", "권담", "이태은", "박시윤", 
    "송서윤", "김유주", "손다희", "김세영", "김민승", "유지아", "조성준", 
    "김하람", "최승아", "진시우", "이주빈", "이진서", "최연아", "박기범", 
    "김건희", "김규리"
]

st.set_page_config(page_title="쑤샘영어 스마트 시스템", layout="wide")

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["선생님 입력용", "학부모 조회용"])

if menu == "선생님 입력용":
    st.title("🎓 쑤샘영어 스마트 평가 시스템")
    
    # 연결 상태 표시
    if connection_success:
        st.success("✅ 구글 시트 연결 완료!")
    else:
        st.error(f"❌ 구글 시트 연결 실패: {error_msg}")
        st.info("바탕화면에 'credentials.json' 파일이 있는지 확인해 주세요.")

    pw = st.sidebar.text_input("관리자 비밀번호", type="password")
    if pw == "1234":
        with st.form("ssusaem_final_form", clear_on_submit=True):
            # 1. 기본 정보
            col1, col2 = st.columns(2)
            with col1:
                name = st.selectbox("👤 학생 이름", STUDENT_LIST)
                date = st.date_input("📅 평가 날짜", datetime.now())
            with col2:
                grade = st.selectbox("🏫 구분", ["초등", "중등"])
                homework = st.radio("📚 과제 여부", ["완료", "미흡", "미완료"], horizontal=True)
            
            attendance = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            st.markdown("---")
            
            # 2. 테스트 결과
            st.markdown("### 📊 테스트 결과")
            v_c1, v_c2, v_c3 = st.columns(3)
            v_t = v_c1.number_input("단어 전체 문항", value=60)
            v_1 = v_c2.number_input("단어 1차 맞은 개수", value=0)
            v_2 = v_c3.number_input("단어 2차 맞은 개수", value=0)
            
            l_c1, l_c2 = st.columns(2)
            l_1 = l_c1.number_input("듣기 1차 점수", value=0)
            l_2 = l_c2.number_input("듣기 2차 점수", value=0)
            st.markdown("---")
            
            # 3. 영역별 성취도 (나란히 배치)
            st.markdown("### 📑 영역별 성취도")
            r_col1, r_col2 = st.columns([4, 1])
            with r_col1: r_con = st.text_input("리딩 수업 내용", placeholder="교재명 및 진도")
            with r_col2: r_p = st.selectbox("수행도", ["우수", "보통", "노력요함"], key="rp")
            
            g_col1, g_col2 = st.columns([4, 1])
            with g_col1: g_con = st.text_input("문법 수업 내용", placeholder="진도 및 핵심 개념")
            with g_col2: g_p = st.selectbox("수행도", ["우수", "보통", "노력요함"], key="gp")
            
            st.markdown("---")
            
            # 4. 코멘트 및 사진
            st.markdown("### 📝 선생님 코멘트 & 자료 첨부")
            comment = st.text_area("학부모님께 전달할 소견", height=100)
            uploaded_file = st.file_uploader("📷 사진 첨부 (선택)", type=['png', 'jpg', 'jpeg'])
            
            if uploaded_file:
                st.image(uploaded_file, caption="업로드 대기 중", width=250)
            
            submit = st.form_submit_button("평가서 저장 및 구글 시트 전송")
            
            if submit:
                if connection_success:
                    try:
                        new_row = [str(date), name, grade, homework, attendance, v_t, v_1, v_2, l_1, l_2, r_con, r_p, g_con, g_p, comment]
                        sheet.append_row(new_row)
                        st.success(f"🎉 {name} 학생의 기록이 구글 시트에 저장되었습니다!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"전송 중 오류 발생: {e}")
                else:
                    st.error("구글 시트와 연결되어 있지 않아 저장할 수 없습니다.")
    else:
        st.info("비밀번호를 입력하시면 시스템이 활성화됩니다.")
else:
    st.header("🔍 학생 평가 결과 조회")
    search_name = st.selectbox("학생 이름을 선택하세요", ["이름 선택"] + STUDENT_LIST)