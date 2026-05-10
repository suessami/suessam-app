import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- [쑤샘영어: 연결 설정 (항목별 방식)] ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # 금고(Secrets)에서 정보를 가져옵니다
    creds_data = st.secrets["gcp_service_account"]
    # 딕셔너리로 변환
    creds_dict = {
        "type": creds_data["type"],
        "project_id": creds_data["project_id"],
        "private_key_id": creds_data["private_key_id"],
        "private_key": creds_data["private_key"].replace("\\n", "\n"),
        "client_email": creds_data["client_email"],
        "client_id": creds_data["client_id"],
        "auth_uri": creds_data["auth_uri"],
        "token_uri": creds_data["token_uri"],
        "auth_provider_x509_cert_url": creds_data["auth_provider_x509_cert_url"],
        "client_x509_cert_url": creds_data["client_x509_cert_url"]
    }
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    SHEET_ID = "1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE"
    sheet = client.open_by_key(SHEET_ID).sheet1
    connection_success = True
except Exception as e:
    st.error(f"⚠️ 연결 실패: {e}")
    connection_success = False

# 학생 명단
STUDENT_LIST = ["권도해", "이재민", "송연주", "이다원", "송하준", "허민우", "이소미", "경지윤", "정주안", "천준영", "하윤성", "권담", "이태은", "박시윤", "송서윤", "김유주", "손다희", "김세영", "김민승", "유지아", "조성준", "김하람", "최승아", "진시우", "이주빈", "이진서", "최연아", "박기범", "김건희", "김규리"]

st.set_page_config(page_title="쑤샘영어 스마트 시스템", layout="wide")

menu = st.sidebar.selectbox("메뉴 선택", ["선생님 입력용", "학부모 조회용"])

if menu == "선생님 입력용":
    st.title("🎓 쑤샘영어 스마트 평가 시스템")
    pw = st.sidebar.text_input("관리자 비밀번호", type="password")
    if pw == "1234":
        col_n, col_g = st.columns(2)
        with col_n: name = st.selectbox("👤 학생 이름", STUDENT_LIST)
        with col_g: grade = st.selectbox("🏫 구분", ["초등", "중등"])
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            homework = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            attendance = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            st.markdown("### 📊 테스트 결과")
            v1, v2, v3 = st.columns(3)
            v_t = v1.number_input("단어 전체 문항", 60); v_1 = v2.number_input("단어 1차 맞은 개수", 0); v_2 = v3.number_input("단어 2차 맞은 개수", 0)
            l_1, l_2 = 0, 0
            if grade == "초등":
                lc1, lc2 = st.columns(2)
                l_1 = lc1.number_input("듣기 1차 점수", 0, 100); l_2 = lc2.number_input("듣기 2차 점수", 0, 100)
            else:
                lc1, lc2, lc3, lc4 = st.columns(4)
                m1_t = lc1.number_input("1차 전체 문항", 1, 100, 20); m1_c = lc2.number_input("1차 맞은 개수", 0, 100, 0)
                m2_t = lc3.number_input("2차 전체 문항", 1, 100, 20); m2_c = lc4.number_input("2차 맞은 개수", 0, 100, 0)
                l_1 = round((m1_c / m1_t) * 100); l_2 = round((m2_c / m2_t) * 100)
            st.markdown("### 📑 영역별 성취도")
            r1, r2 = st.columns([3, 1]); r_con = r1.text_input("리딩 수업 내용"); r_p = r2.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            g1, g2 = st.columns([3, 1]); g_con = g1.text_input("문법 수업 내용"); g_p = g2.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])
            uploaded_file = st.file_uploader("학습 사진 선택", type=['png', 'jpg', 'jpeg'])
            comment = st.text_area("📝 선생님 코멘트")
            submit = st.form_submit_button("평가서 저장 및 전송")
            if submit and connection_success:
                photo_status = "사진있음" if uploaded_file else "없음"
                new_row = [str(date), name, grade, homework, attendance, v_t, v_1, v_2, l_1, l_2, r_con, r_p, g_con, g_p, comment, photo_status]
                sheet.append_row(new_row); st.success(f"🎉 {name} 학생 기록 저장 완료!")

elif menu == "학부모 조회용":
    st.title("🔍 학생 평가 결과 조회")
    search_name = st.selectbox("학생 이름을 선택하세요", ["이름 선택"] + STUDENT_LIST)
    if search_name != "이름 선택" and connection_success:
        data = sheet.get_all_records(); df = pd.DataFrame(data); student_data = df[df['학생 이름'] == search_name]
        if not student_data.empty:
            for i in range(len(student_data)-1, -1, -1):
                row = student_data.iloc[i]
                with st.expander(f"📅 {row['평가 날짜']} 리포트 (클릭)"):
                    st.markdown("#### 📝 기본 정보 및 테스트")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**과제:** {row['과제 여부']}"); c2.write(f"**출결:** {row['출결']}"); c3.write(f"**단어:** {row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                    l_text = f"{row['듣기 1차 점수']}점" if row['듣기 2차 점수'] == 0 else f"1차:{row['듣기 1차 점수']} / 2차:{row['듣기 2차 점수']}"
                    c4.write(f"**듣기:** {l_text}")
                    st.markdown("---"); st.markdown("#### 📚 수업 내용 및 성취도")
                    if row['리딩 수행도'] != "-":
                        rc1, rc2 = st.columns([3, 1]); rc1.write(f"**리딩:** {row['리딩 수업 내용']}"); rc2.write(f"**수행도:** {row['리딩 수행도']}")
                    if row['문법 수행도'] != "-":
                        gc1, gc2 = st.columns([3, 1]); gc1.write(f"**문법:** {row['문법 수업 내용']}"); gc2.write(f"**수행도:** {row['문법 수행도']}")
                    st.info(f"💡 **선생님 소견:** {row['코멘트']}")
        else: st.warning("등록된 데이터가 없습니다.")