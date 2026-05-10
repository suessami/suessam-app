import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 앱 설정 & 디지털 대문 디자인] ---
st.set_page_config(page_title="쑤샘영어 스마트 리포트", page_icon="🎓", layout="wide")

# 사진 대신 코드로 만든 세련된 블루 배너입니다.
st.markdown("""
    <div style="background: linear-gradient(to right, #0f172a, #1e293b, #0f172a); 
                padding: 30px; border-radius: 15px; border: 2px solid #38bdf8; 
                text-align: center; box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.3);">
        <h1 style="color: #facc15; margin-bottom: 5px; font-family: 'Pretendard', sans-serif;">
            🎓 쑤샘영어 SMART REPORT
        </h1>
        <p style="color: #38bdf8; font-size: 1.2rem; margin-top: 0;">
            SUE ENGLISH INNOVATION SYSTEM
        </p>
        <div style="background-color: rgba(56, 189, 248, 0.1); padding: 10px; border-radius: 10px; color: white;">
            혁신적인 우리 아이 AI 스마트 평가 리포트
        </div>
    </div>
    """, unsafe_allow_html=True)
st.write("") # 간격 띄우기

# --- [2. 학생 정보 & 비밀번호 DB (30명 완벽 매칭)] ---
STUDENT_INFO = {
    "권도해": "7236", "이재민": "2052", "송연주": "8526", "이다원": "6765", "송하준": "1703",
    "허민우": "7007", "이소미": "5520", "경지윤": "6671", "정주안": "0321", "천준영": "3837",
    "하윤성": "2256", "권담": "4767", "이태은": "4848", "박시윤": "0354", "송서윤": "0548",
    "김유주": "3698", "손다희": "7713", "김세영": "9106", "김민승": "4227", "유지아": "0975",
    "조성준": "0405", "김하람": "4551", "최승아": "3857", "진시우": "5008", "이주빈": "6765",
    "이진서": "1696", "최연아": "8550", "박기범": "8390", "김건희": "9345", "김규리": "9345", "쑤새미": "9603"
}
STUDENT_LIST = sorted(list(STUDENT_INFO.keys()))

# --- [3. 구글 시트 연결] ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds_data = st.secrets["gcp_service_account"]
    creds_dict = {
        "type": creds_data["type"], "project_id": creds_data["project_id"],
        "private_key_id": creds_data["private_key_id"],
        "private_key": creds_data["private_key"].replace("\\n", "\n"),
        "client_email": creds_data["client_email"], "client_id": creds_data["client_id"],
        "auth_uri": creds_data["auth_uri"], "token_uri": creds_data["token_uri"],
        "auth_provider_x509_cert_url": creds_data["auth_provider_x509_cert_url"],
        "client_x509_cert_url": creds_data["client_x509_cert_url"]
    }
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE").sheet1
    connection_success = True
except Exception as e:
    st.error(f"연결 에러: {e}")
    connection_success = False

# --- [4. 앱 메뉴 구성] ---
menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# [A. 선생님 입력용]
if menu == "선생님 입력용":
    st.title("🎓 성적 입력 시스템 (관리자)")
    if st.sidebar.text_input("비밀번호", type="password") == "1234":
        name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            hw = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            v_t = st.number_input("단어 전체 문항", 60); v_1 = st.number_input("단어 맞은 개수", 0)
            l_1 = st.number_input("듣기 점수", 0, 100)
            st.markdown("---")
            r_con = st.text_input("리딩 수업 내용"); r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            g_con = st.text_input("문법 수업 내용"); g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])
            comment = st.text_area("종합 선생님 코멘트")
            if st.form_submit_button("평가서 저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                # f"'{pw}"로 앞자리 0을 지켜서 저장합니다.
                new_row = [str(date), name, "구분", hw, att, v_t, v_1, 0, l_1, 0, r_con, r_p, g_con, g_p, comment, pw]
                sheet.append_row(new_row)
                st.success(f"🎉 {name} 저장 완료! (비번: {pw})")

# [B. 학부모 조회용]
elif menu == "학부모 조회용":
    st.title("🔍 쑤샘영어 우리 아이 리포트 조회")
    st.info("아이 이름과 등록된 비밀번호(어머니 핸드폰 뒷자리)를 입력해 주세요.")
    c1, c2 = st.columns(2)
    with c1: name_in = st.text_input("👤 학생 이름")
    with c2: pw_in = st.text_input("🔑 비밀번호", type="password")
    
    if name_in and pw_in and connection_success:
        try:
            all_v = sheet.get_all_values()
            df = pd.DataFrame(all_v[1:], columns=all_v[0])
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str) == str(pw_in))]
            if not res.empty:
                st.success(f"✅ {name_in} 학생의 리포트입니다.")
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인"):
                        # 모든 정보를 깔끔하게 보여줍니다.
                        st.markdown("#### 📊 학습 현황")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("과제", row['과제 여부'])
                        col2.metric("출결", row['출결'])
                        col3.metric("단어", f"{row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                        col4.metric("듣기", f"{row['듣기 1차 점수']}점")
                        st.markdown("---")
                        st.markdown("#### 📚 수업 내용")
                        if row['리딩 수업 내용']: st.write(f"**리딩:** {row['리딩 수업 내용']} ({row['리딩 수행도']})")
                        if row['문법 수업 내용']: st.write(f"**문법:** {row['문법 수업 내용']} ({row['문법 수행도']})")
                        st.warning(f"📝 **선생님 소견:** {row['코멘트']}")
            else: st.error("정보가 일치하지 않습니다.")
        except: st.error("조회 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")