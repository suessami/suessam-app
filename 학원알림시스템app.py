import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- [쑤샘영어: 연결 설정] ---
current_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(current_dir, "credentials.json")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
    client = gspread.authorize(creds)
    SHEET_ID = "1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE"
    sheet = client.open_by_key(SHEET_ID).sheet1
    connection_success = True
except:
    connection_success = False

STUDENT_LIST = ["권도해", "이재민", "송연주", "이다원", "송하준", "허민우", "이소미", "경지윤", "정주안", "천준영", "하윤성", "권담", "이태은", "박시윤", "송서윤", "김유주", "손다희", "김세영", "김민승", "유지아", "조성준", "김하람", "최승아", "진시우", "이주빈", "이진서", "최연아", "박기범", "김건희", "김규리"]

st.set_page_config(page_title="쑤샘영어 스마트 시스템", layout="wide")

menu = st.sidebar.selectbox("메뉴 선택", ["선생님 입력용", "학부모 조회용"])

if menu == "선생님 입력용":
    st.title("🎓 쑤샘영어 스마트 평가 시스템")
    # (기존 입력 폼 코드는 동일합니다)
    pw = st.sidebar.text_input("관리자 비밀번호", type="password")
    if pw == "1234":
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.selectbox("👤 학생 이름", STUDENT_LIST)
                date = st.date_input("📅 평가 날짜", datetime.now())
            with col2:
                grade = st.selectbox("🏫 구분", ["초등", "중등"])
                homework = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            
            attendance = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            v1, v2, v3 = st.columns(3)
            v_t, v_1, v_2 = v1.number_input("단어전체", 60), v2.number_input("1차", 0), v3.number_input("2차", 0)
            
            comment = st.text_area("📝 코멘트")
            submit = st.form_submit_button("평가서 저장")
            
            if submit and connection_success:
                sheet.append_row([str(date), name, grade, homework, attendance, v_t, v_1, v_2, comment])
                st.success("저장 완료!")

elif menu == "학부모 조회용":
    st.title("🔍 학생 평가 결과 조회")
    search_name = st.selectbox("학생 이름을 선택하세요", ["이름 선택"] + STUDENT_LIST)
    
    if search_name != "이름 선택" and connection_success:
        # 구글 시트 데이터 가져오기
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 선택한 학생 데이터만 필터링
        student_data = df[df['학생 이름'] == search_name]
        
        if not student_data.empty:
            st.subheader(f"✨ {search_name} 학생의 학습 리포트")
            # 최신순으로 보여주기
            for i in range(len(student_data)-1, -1, -1):
                row = student_data.iloc[i]
                with st.expander(f"📅 {row['평가 날짜']} 평가 결과 (클릭해서 보기)"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("과제", row['과제 여부'])
                    c2.metric("출결", row['출결'])
                    c3.metric("단어 성취도", f"{row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                    st.info(f"📝 선생님 소견: {row['코멘트']}")
        else:
            st.warning("아직 등록된 평가 데이터가 없습니다.")