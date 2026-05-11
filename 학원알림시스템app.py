import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 앱 설정 & 디자인] ---
# 아이폰이 가장 잘 인식하는 '직접 이미지 링크'입니다.
# (원장님이 깃허브에 올리신 파일의 Raw 주소를 제가 미리 가공해 두었습니다)
SUE_LOGO_URL = "https://raw.githubusercontent.com/sue-reading/sue-report/main/S_Logo_transparent_v2.png"

st.set_page_config(
    page_title="쑤샘영어 스마트 리포트",
    page_icon=SUE_LOGO_URL, 
    layout="wide"
)

# 아이폰 '홈 화면에 추가' 시 노션을 밀어내고 우리 로고를 강제 적용하는 코드
st.markdown(f"""
    <link rel="apple-touch-icon" href="{SUE_LOGO_URL}">
    <link rel="icon" href="{SUE_LOGO_URL}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="쑤샘영어">
    """, unsafe_allow_html=True)

# ... (이하 기존 코드 동일)
st.markdown("""
    <div style="background: linear-gradient(to right, #0f172a, #1e293b, #0f172a); 
                padding: 30px; border-radius: 15px; border: 2px solid #38bdf8; 
                text-align: center; box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.3);">
        <h1 style="color: #facc15; margin-bottom: 5px;">
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
st.write("") 

# --- [2. 학생 정보 & 비밀번호 DB] ---
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
# (원장님 코드와 동일하므로 연결 로직 유지)
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

menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# [A. 선생님 입력용]
if menu == "선생님 입력용":
    st.title("🎓 성적 입력 시스템 (관리자)")
    if st.sidebar.text_input("관리자 비밀번호", type="password") == "1234":
        name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            level = st.radio("🏫 학교급 선택", ["초등", "중등"], horizontal=True)
            hw = st.radio("📚 과제 여부", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결 상태", ["양호", "지각", "결석"], horizontal=True)
            
            st.markdown("### 📊 단어 & 듣기")
            v_t = st.number_input("단어 전체 문항", value=60)
            col1, col2 = st.columns(2)
            with col1: v_1 = st.number_input("단어 1차 맞은 개수", 0)
            with col2: v_2 = st.number_input("단어 2차 맞은 개수", 0)
            l_1 = st.number_input("듣기 점수", 0, 100)

            st.markdown("---")
            st.subheader("📖 수업 상세 평가")
            r_con = st.text_input("리딩 수업 내용")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            reading_voca = st.selectbox("📚 리딩 단어 암기", ["열심히 외움", "대충 외움", "공부한 노력이 보이지 않음"])
            reading_sent = st.selectbox("✍️ 리딩 지문 영작/해석", ["열심히 공부했음", "조금 더 공부하기", "공부한 노력이 보이지 않음"])
            
            g_con = st.text_input("문법 수업 내용")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])

            writing_feedback = st.text_area("✒️ 영어홀릭 라이팅 피드백")
            comment = st.text_area("🌟 선생님 코멘트")

            if st.form_submit_button("평가서 저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                new_row = [str(date), name, level, hw, att, v_t, v_1, v_2, l_1, 0, r_con, r_p, g_con, g_p, reading_voca, reading_sent, writing_feedback, comment, pw]
                sheet.append_row(new_row)
                st.success(f"🎉 {name}({level}) 리포트 저장 완료!")

# [B. 학부모 조회용]
elif menu == "학부모 조회용":
    st.title("🔍 쑤샘영어 우리 아이 리포트 조회")
    c1, c2 = st.columns(2)
    with c1: name_in = st.text_input("👤 학생 이름")
    with c2: pw_in = st.text_input("🔑 비밀번호", type="password")
    
    if name_in and pw_in and connection_success:
        try:
            all_v = sheet.get_all_values()
            df = pd.DataFrame(all_v[1:], columns=all_v[0])
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str).str.strip() == str(pw_in).strip())]
            
            if not res.empty:
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인"):
                        st.markdown("#### 📊 학습 현황")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("과제", row['과제 여부'])
                        m2.metric("출결", row['출결'])
                        
                        vt = int(row['단어 전체 문항']) if row['단어 전체 문항'] else 0
                        v1 = int(row['단어 1차 맞은 개수']) if row['단어 1차 맞은 개수'] else 0
                        v2 = int(row['단어 2차 맞은 개수']) if row['단어 2차 맞은 개수'] else 0
                        
                        if row['구분'] == "중등" and vt > 0:
                            score = round((v1/vt)*100)
                            v_delta = f"{v1}/{vt}"
                            if v2 > 0: v_delta += f" (2차:{v2})"
                            m3.metric("단어 점수", f"{score}점", v_delta)
                        else:
                            v_val = f"{v1}/{vt}"
                            if v2 > 0: v_val += f" (2차:{v2})"
                            m3.metric("단어", v_val)
                        m4.metric("듣기", f"{row['듣기 1차 점수']}점")
                        
                        st.markdown("---")
                        st.write(f"**📚 리딩 단어:** {row['리딩 단어']}")
                        st.write(f"**✍️ 리딩 영작/해석:** {row['리딩 지문 영작 및 해석']}")
                        st.info(f"**📝 라이팅 피드백:**\n\n{row['영어홀릭 라이팅']}")
                        st.warning(f"📝 **종합 소견:** {row['코멘트']}")
                
                # --- [카톡 스타일 노란색 안내 박스] ---
                st.divider()
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; background-color: #FEE500; border-radius: 12px; padding: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
                        <div style="margin-right: 15px;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/KakaoTalk_logo.svg" width="40">
                        </div>
                        <div style="color: #191919; font-weight: bold; font-size: 16px; line-height: 1.5;">
                            리포트 보시고 궁금하신 점은<br>
                            평소처럼 카톡으로 편하게 말씀해 주세요! 😊
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            else: st.error("정보가 일치하지 않습니다.")
        except Exception as e: 
            st.error(f"오류가 발생했습니다: {e}")