import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title="쑤샘영어 스마트 리포트", 
    page_icon="🎓", 
    layout="wide"

# --- [1. 학생 정보 & 비밀번호 DB (원장님 요청 30명 전체)] ---
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
    # 쑤샘영어 구글 시트 ID (변경 금지)
    sheet = client.open_by_key("1cI7yQIne4ZWdICRhVoqw18P16ZN81kT5LOnDN1ipfhE").sheet1
    connection_success = True
except Exception as e:
    st.error(f"연결 에러: {e}")
    connection_success = False

# --- [3. 메인 화면 구성] ---
st.set_page_config(page_title="쑤샘영어 스마트 리포트", layout="wide")
menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# [A. 선생님 입력용 화면]
if menu == "선생님 입력용":
    st.title("🎓 성적 입력 시스템 (관리자)")
    if st.sidebar.text_input("관리자 비밀번호", type="password") == "1234":
        col_n, col_g = st.columns(2)
        with col_n: name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        with col_g: grade = st.selectbox("🏫 구분", ["초등", "중등"])
        
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            hw = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            
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
                m1_t = lc1.number_input("1차전체", 20); m1_c = lc2.number_input("1차맞은", 0)
                m2_t = lc3.number_input("2차전체", 20); m2_c = lc4.number_input("2차맞은", 0)
                l_1 = round((m1_c/m1_t)*100 if m1_t > 0 else 0)
                l_2 = round((m2_c/m2_t)*100 if m2_t > 0 else 0)

            st.markdown("---")
            st.subheader("📝 영역별 성취도")
            r_con = st.text_input("리딩 수업 내용")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            g_con = st.text_input("문법 수업 내용")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])
            comment = st.text_area("종합 선생님 코멘트")
            
            if st.form_submit_button("평가서 저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                # P열(16번째 칸)에 비밀번호 저장 (f"'{pw}"로 앞자리 0 보존)
                new_row = [str(date), name, grade, hw, att, v_t, v_1, v_2, l_1, l_2, r_con, r_p, g_con, g_p, comment, f"'{pw}"]
                sheet.append_row(new_row)
                st.success(f"🎉 {name} 학생 저장 완료! (비밀번호: {pw})")

# [B. 학부모 조회용 화면]
elif menu == "학부모 조회용":
    st.title("🔍 쑤샘영어 우리 아이 리포트 조회")
    st.info("아이 이름과 등록된 비밀번호(어머니 핸드폰 뒷자리)를 입력해 주세요.")
    
    col1, col2 = st.columns(2)
    with col1: name_in = st.text_input("👤 학생 이름", placeholder="이름 입력")
    with col2: pw_in = st.text_input("🔑 비밀번호", type="password", placeholder="뒷자리 4자리")
    
    if name_in and pw_in and connection_success:
        try:
            # 시트의 모든 데이터를 가져와서 표(DataFrame)로 변환
            all_v = sheet.get_all_values()
            df = pd.DataFrame(all_v[1:], columns=all_v[0])
            
            # 이름과 비밀번호가 모두 일치하는 행 찾기
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str) == str(pw_in))]
            
            if not res.empty:
                st.success(f"✅ {name_in} 학생의 리포트를 불러왔습니다.")
                for _, row in res.iloc[::-1].iterrows(): # 최신순 정렬
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인"):
                        # 1. 학습 기본
                        st.markdown("#### 📊 학습 태도 및 테스트")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.write(f"**과제:** {row['과제 여부']}")
                        c2.write(f"**출결:** {row['출결']}")
                        c3.write(f"**단어:** {row['단어 1차 맞은 개수']}/{row['단어 전체 문항']}")
                        # 듣기 점수 표시 (2차가 있으면 같이 표시)
                        l_val = f"{row['듣기 1차 점수']}점"
                        if row['듣기 2차 점수'] != '0' and row['듣기 2차 점수'] != '':
                            l_val += f" (2차: {row['듣기 2차 점수']}점)"
                        c4.write(f"**듣기:** {l_val}")
                        
                        st.markdown("---")
                        # 2. 영역별 상세
                        st.markdown("#### 📚 영역별 수업 내용")
                        if row['리딩 수업 내용']:
                            st.write(f"**리딩:** {row['리딩 수업 내용']} (수행도: {row['리딩 수행도']})")
                        if row['문법 수업 내용']:
                            st.write(f"**문법:** {row['문법 수업 내용']} (수행도: {row['문법 수행도']})")
                        
                        st.warning(f"📝 **선생님 소견:** {row['코멘트']}")
            else:
                st.error("입력하신 이름 또는 비밀번호가 일치하지 않습니다.")
        except Exception as e:
            st.error(f"데이터 조회 중 오류 발생: {e}")