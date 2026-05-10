import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 학생 정보 및 비밀번호 데이터베이스] ---
# 원장님이 주신 명단과 번호를 모두 등록했습니다. 
# 이제 원장님은 이름만 고르시면 번호는 코드가 알아서 시트에 적어줍니다.
STUDENT_INFO = {
    "권도해": "7236", "이재민": "2052", "송연주": "8526", "이다원": "6765", "송하준": "1703",
    "허민우": "7007", "이소미": "5520", "경지윤": "6671", "정주안": "0321", "천준영": "3837",
    "하윤성": "2256", "권담": "4767", "이태은": "4848", "박시윤": "0354", "송서윤": "0548",
    "김유주": "3698", "손다희": "7713", "김세영": "9106", "김민승": "4227", "유지아": "0975",
    "조성준": "0405", "김하람": "4551", "최승아": "3857", "진시우": "5008", "이주빈": "6765",
    "이진서": "1696", "최연아": "8550", "박기범": "8390", "김건희": "9345", "김규리": "9345"
}
STUDENT_LIST = sorted(list(STUDENT_INFO.keys()))

# --- [2. 구글 시트 연결 설정] ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # 스트림릿 Secrets(금고)에서 정보를 가져옵니다.
    creds_data = st.secrets["gcp_service_account"]
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
    
    # 쑤샘영어 구글 시트 ID
    SHEET_ID = "1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE"
    sheet = client.open_by_key(SHEET_ID).sheet1
    connection_success = True
except Exception as e:
    st.error(f"⚠️ 연결 실패: {e}")
    connection_success = False

# --- [3. 메인 화면 구성] ---
st.set_page_config(page_title="쑤샘영어 스마트 피드백", layout="wide")
menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# [선생님 입력용 화면]
if menu == "선생님 입력용":
    st.title("🎓 쑤샘영어 성적 입력 시스템")
    admin_pw = st.sidebar.text_input("관리자 비밀번호", type="password")
    
    if admin_pw == "1234":  # 관리자 비밀번호
        col_n, col_g = st.columns(2)
        with col_n: name = st.selectbox("👤 학생 이름 선택", STUDENT_LIST)
        with col_g: grade = st.selectbox("🏫 구분", ["초등", "중등"])
        
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            homework = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            attendance = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            
            st.markdown("---")
            st.subheader("📊 테스트 결과")
            v1, v2, v3 = st.columns(3)
            v_t = v1.number_input("단어 전체 문항", 60)
            v_1 = v2.number_input("1차 맞은 개수", 0)
            v_2 = v3.number_input("2차 맞은 개수", 0)
            
            l_1, l_2 = 0, 0
            if grade == "초등":
                lc1, lc2 = st.columns(2)
                l_1 = lc1.number_input("듣기 1차 점수", 0, 100)
                l_2 = lc2.number_input("듣기 2차 점수", 0, 100)
            else:
                lc1, lc2, lc3, lc4 = st.columns(4)
                m1_t = lc1.number_input("1차 전체문항", 20); m1_c = lc2.number_input("1차 맞은개수", 0)
                m2_t = lc3.number_input("2차 전체문항", 20); m2_c = lc4.number_input("2차 맞은개수", 0)
                l_1 = round((m1_c/m1_t)*100 if m1_t > 0 else 0)
                l_2 = round((m2_c/m2_t)*100 if m2_t > 0 else 0)
            
            st.markdown("---")
            st.subheader("📝 영역별 코멘트")
            r_con = st.text_input("리딩 수업 내용")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            g_con = st.text_input("문법 수업 내용")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])
            comment = st.text_area("종합 선생님 코멘트")
            
            submit = st.form_submit_button("평가서 저장하기")
            
            if submit and connection_success:
                # [자동 매칭!] 학생 장부에서 비밀번호를 자동으로 찾아 시트에 저장합니다.
                auto_pw = STUDENT_INFO.get(name, "0000")
                
                # 시트 열 순서에 맞춰 데이터 구성 (총 17개 열)
                new_row = [
                    str(date), name, grade, homework, attendance, 
                    v_t, v_1, v_2, l_1, l_2, 
                    r_con, r_p, g_con, g_p, comment, "없음", auto_pw
                ]
                sheet.append_row(new_row)
                st.success(f"🎉 {name} 학생의 기록이 저장되었습니다! (학부모 비번: {auto_pw})")

# [학부모 조회용 화면]
elif menu == "학부모 조회용":
    st.title("🔍 쑤샘영어 우리 아이 리포트 조회")
    st.info("아이 이름과 등록된 비밀번호(어머니 핸드폰 뒷자리)를 입력해 주세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("👤 학생 이름", placeholder="이름을 입력하세요")
    with col2:
        search_pw = st.text_input("🔑 비밀번호 (4자리)", type="password", placeholder="번호 뒷자리")
    
    if search_name and search_pw and connection_success:
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # [보안 확인] 이름과 비밀번호가 모두 맞아야만 데이터를 필터링합니다.
            student_data = df[(df['학생 이름'] == search_name) & (df['비밀번호'].astype(str) == str(search_pw))]
            
            if not student_data.empty:
                st.success(f"✅ {search_name} 학생의 평가 기록을 찾았습니다.")
                # 최신 날짜가 위로 오도록 역순으로 보여줍니다.
                for i in range(len(student_data)-1, -1, -1):
                    row = student_data.iloc[i]
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인하기"):
                        st.markdown("#### 📊 학습 현황")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("과제", row['과제 여부'])
                        c2.metric("출결", row['출결'])
                        c3.metric("단어", f"{row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                        l_val = f"{row['듣기 1차 점수']}점" if row['듣기 2차 점수'] == 0 else f"1차:{row['듣기 1차 점수']} / 2차:{row['듣기 2차 점수']}"
                        c4.metric("듣기", l_val)
                        
                        st.markdown("---")
                        st.markdown("#### 📚 수업 성취도")
                        if row['리딩 수행도'] != "-":
                            st.write(f"**리딩:** {row['리딩 수업 내용']} ({row['리딩 수행도']})")
                        if row['문법 수행도'] != "-":
                            st.write(f"**문법:** {row['문법 수업 내용']} ({row['문법 수행도']})")
                        
                        st.warning(f"💡 **선생님 소견:** {row['코멘트']}")
            else:
                st.error("입력하신 정보와 일치하는 기록이 없습니다. 이름과 비밀번호를 다시 확인해 주세요.")
        except Exception as e:
            st.error("데이터를 가져오는 중에 오류가 발생했습니다.")