import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 앱 설정 & 로고 강제 고정] ---
# 아이폰과 카톡이 "이건 완전히 새로운 주소다!"라고 착각하게 v=40을 붙였습니다.
SUE_LOGO_URL = "https://raw.githubusercontent.com/sue-reading/sue-report/main/S_Logo_transparent_v2.png?v=40"

st.set_page_config(
    page_title="쑤샘영어 스마트 리포트",
    page_icon=SUE_LOGO_URL,
    layout="wide"
)

# 아이폰 홈 화면 + 문자/카톡 미리보기를 동시에 잡는 '헤드' 설정
st.markdown(f"""
    <head>
        <link rel="apple-touch-icon" href="{SUE_LOGO_URL}">
        <link rel="apple-touch-icon-precomposed" href="{SUE_LOGO_URL}">
        <link rel="icon" href="{SUE_LOGO_URL}">
        <meta property="og:title" content="🎓 쑤샘영어 SMART REPORT">
        <meta property="og:description" content="우리 아이 AI 스마트 평가 리포트">
        <meta property="og:image" content="{SUE_LOGO_URL}">
        <meta property="og:type" content="website">
        <meta name="apple-mobile-web-app-title" content="쑤샘영어">
        <meta name="apple-mobile-web-app-capable" content="yes">
    </head>
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * {{ font-family: 'Pretendard', sans-serif !important; }}
        /* 메인 배너 스타일 */
        .main-header {{
            background: linear-gradient(to right, #0f172a, #1e293b, #0f172a); 
            padding: 30px; border-radius: 15px; border: 2px solid #38bdf8; 
            text-align: center; box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.3);
            margin-bottom: 25px;
        }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1 style="color: #facc15; margin-bottom: 5px;">🎓 쑤샘영어 SMART REPORT</h1>
        <p style="color: #38bdf8; font-size: 1.2rem; margin-top: 0;">SUE ENGLISH INNOVATION SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)

# --- [2. 학생 데이터 & 시트 연결] ---
STUDENT_INFO = {
    "권도해": "7236", "이재민": "2052", "송연주": "8526", "이다원": "6765", "송하준": "1703",
    "허민우": "7007", "이소미": "5520", "경지윤": "6671", "정주안": "0321", "천준영": "3837",
    "하윤성": "2256", "권담": "4767", "이태은": "4848", "박시윤": "0354", "송서윤": "0548",
    "김유주": "3698", "손다희": "7713", "김세영": "9106", "김민승": "4227", "유지아": "0975",
    "조성준": "0405", "김하람": "4551", "최승아": "3857", "진시우": "5008", "이주빈": "6765",
    "이진서": "1696", "최연아": "8550", "박기범": "8390", "김건희": "9345", "김규리": "9345", "쑤새미": "9603"
}
STUDENT_LIST = sorted(list(STUDENT_INFO.keys()))

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
    st.error(f"연결 오류: {e}")
    connection_success = False

# --- [3. 메뉴 & 조회/입력 로직] ---
menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

if menu == "선생님 입력용":
    st.title("🎓 성적 입력")
    if st.sidebar.text_input("비밀번호", type="password") == "1234":
        name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 날짜", datetime.now())
            level = st.radio("🏫 구분", ["초등", "중등"], horizontal=True)
            hw = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            
            st.markdown("### 📊 성적 데이터")
            v_t = st.number_input("단어 전체", value=60)
            c1, c2 = st.columns(2)
            with c1: v_1 = st.number_input("1차 맞은 개수", 0)
            with c2: v_2 = st.number_input("2차 맞은 개수", 0)
            l_1 = st.number_input("듣기 점수", 0, 100)

            r_con = st.text_input("리딩 내용")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            reading_voca = st.selectbox("📚 리딩 단어", ["열심히 외움", "대충 외움", "노력 필요"])
            reading_sent = st.selectbox("✍️ 리딩 영작", ["열심히 했음", "조금 더 공부", "노력 필요"])
            
            g_con = st.text_input("문법 내용")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])

            writing_feedback = st.text_area("✒️ 라이팅 피드백")
            comment = st.text_area("🌟 종합 소견")

            if st.form_submit_button("저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                new_row = [str(date), name, level, hw, att, v_t, v_1, v_2, l_1, 0, r_con, r_p, g_con, g_p, reading_voca, reading_sent, writing_feedback, comment, pw]
                sheet.append_row(new_row)
                st.success(f"🎉 {name} 리포트 저장 완료!")

elif menu == "학부모 조회용":
    st.title("🔍 우리 아이 리포트 조회")
    ca, cb = st.columns(2)
    with ca: name_in = st.text_input("👤 학생 이름")
    with cb: pw_in = st.text_input("🔑 비밀번호", type="password")
    
    if name_in and pw_in and connection_success:
        try:
            all_v = sheet.get_all_values()
            df = pd.DataFrame(all_v[1:], columns=all_v[0])
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str).str.strip() == str(pw_in).strip())]
            
            if not res.empty:
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트"):
                        st.markdown("#### 📊 학습 현황")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("과제", row['과제 여부'])
                        m2.metric("출결", row['출결'])
                        
                        vt = int(row['단어 전체 문항']) if row['단어 전체 문항'] else 0
                        v1 = int(row['단어 1차 맞은 개수']) if row['단어 1차 맞은 개수'] else 0
                        v2 = int(row['단어 2차 맞은 개수']) if row['단어 2차 맞은 개수'] else 0
                        
                        if row['구분'] == "중등" and vt > 0:
                            score = round((v1/vt)*100)
                            m3.metric("단어 점수", f"{score}점", f"{v1}/{vt}")
                        else:
                            m3.metric("단어", f"{v1}/{vt}")
                        m4.metric("듣기", f"{row['듣기 1차 점수']}점")
                        
                        st.markdown("---")
                        st.info(f"**📝 라이팅 피드백:**\n\n{row['영어홀릭 라이팅']}")
                        st.warning(f"📝 **종합 소견:** {row['코멘트']}")
                
                st.divider()
                st.markdown("""
                    <div style="display: flex; align-items: center; background-color: #FEE500; border-radius: 12px; padding: 20px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/KakaoTalk_logo.svg" width="40" style="margin-right:15px;">
                        <div style="color: #191919; font-weight: bold; font-size: 16px;">
                            궁금하신 점은 평소처럼 카톡으로 편하게 말씀해 주세요! 😊
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.error("정보가 일치하지 않습니다.")
        except Exception as e: st.error(f"오류: {e}")