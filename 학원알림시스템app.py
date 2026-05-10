import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 학생 정보 장부] ---
STUDENT_INFO = {
    "권도해": "7236", "이재민": "2052", "송연주": "8526", "이다원": "6765", "송하준": "1703",
    "허민우": "7007", "이소미": "5520", "경지윤": "6671", "정주안": "0321", "천준영": "3837",
    "하윤성": "2256", "권담": "4767", "이태은": "4848", "박시윤": "0354", "송서윤": "0548",
    "김유주": "3698", "손다희": "7713", "김세영": "9106", "김민승": "4227", "유지아": "0975",
    "조성준": "0405", "김하람": "4551", "최승아": "3857", "진시우": "5008", "이주빈": "6765",
    "이진서": "1696", "최연아": "8550", "박기범": "8390", "김건희": "9345", "김규리": "9345"
}
STUDENT_LIST = sorted(list(STUDENT_INFO.keys()))

# --- [2. 연결 설정] ---
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

# --- [3. 화면 구성] ---
st.set_page_config(page_title="쑤샘영어 스마트 리포트", layout="wide")
menu = st.sidebar.selectbox("메뉴", ["학부모 조회용", "선생님 입력용"])

if menu == "선생님 입력용":
    st.title("🎓 성적 입력 (관리자)")
    if st.sidebar.text_input("비밀번호", type="password") == "1234":
        name = st.selectbox("학생 선택", STUDENT_LIST)
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("날짜", datetime.now())
            hw = st.radio("과제", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("출결", ["양호", "지각", "결석"], horizontal=True)
            v_t = st.number_input("단어전체", 60); v_1 = st.number_input("맞은개수", 0)
            comment = st.text_area("선생님 소견")
            if st.form_submit_button("저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                # P열(16번째 열)이 비밀번호가 되도록 딱 16개의 데이터를 넣습니다.
                new_row = new_row = [str(date), name, "구분", hw, att, v_t, v_1, 0, 0, 0, "", "", "", "", comment, f"'{pw}"]                sheet.append_row(new_row)
                st.success(f"🎉 {name} 저장 완료! (비밀번호: {pw})")

elif menu == "학부모 조회용":
    st.title("🔍 우리 아이 리포트 조회")
    name_in = st.text_input("👤 학생 이름")
    pw_in = st.text_input("🔑 비밀번호 (4자리)", type="password")
    
    if name_in and pw_in and connection_success:
        try:
            # 데이터 가져오기
            all_values = sheet.get_all_values()
            df = pd.DataFrame(all_values[1:], columns=all_values[0])
            
            # 검색 (이름과 비밀번호가 모두 맞아야 함)
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str) == str(pw_in))]
            
            if not res.empty:
                st.success(f"✅ {name_in} 학생의 리포트입니다.")
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트"):
                        st.write(f"**과제:** {row['과제 여부']} | **출결:** {row['출결']}")
                        st.write(f"**단어:** {row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                        st.info(f"📝 {row['코멘트']}")
            else:
                st.error("입력하신 정보가 틀립니다. 이름과 번호를 다시 확인해 주세요.")
        except Exception as e:
            st.error(f"조회 중 오류 발생: {e}")