import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 앱 설정 & 디자인] ---
st.set_page_config(page_title="쑤샘영어 스마트 리포트", page_icon="🎓", layout="wide")

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

# --- [4. 메뉴 구성] ---
menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# [A. 선생님 입력용]
if menu == "선생님 입력용":
    st.title("🎓 성적 입력 시스템")
    if st.sidebar.text_input("비밀번호", type="password") == "1234":
        name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            level = st.radio("🏫 학교급", ["초등", "중등"], horizontal=True)
            hw = st.radio("📚 과제", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결", ["양호", "지각", "결석"], horizontal=True)
            
            st.markdown("### 📊 단어 & 듣기")
            v_t = st.number_input("단어 전체 문항", value=60)
            c1, c2 = st.columns(2)
            with c1: v_1 = st.number_input("단어 1차 맞은 개수", 0)
            with c2: v_2 = st.number_input("단어 2차 맞은 개수", 0)
            l_1 = st.number_input("듣기 1차 점수", 0, 100)

            st.markdown("### 📖 리딩 (Reading)")
            r_con = st.text_input("리딩 수업 내용")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            reading_voca = st.selectbox("📚 리딩 단어 암기", ["열심히 외움", "대충 외움", "공부한 노력이 보이지 않음"])
            reading_sent = st.selectbox("✍️ 리딩 지문 영작/해석", ["열심히 공부했음", "조금 더 공부하기", "공부한 노력이 보이지 않음"])

            st.markdown("### 📝 문법 (Grammar)")
            g_con = st.text_input("문법 수업 내용")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])

            st.markdown("### ✒️ 라이팅 & 코멘트")
            writing_feedback = st.text_area("라이팅 상세 피드백")
            comment = st.text_area("🌟 종합 소견")

            if st.form_submit_button("평가서 저장하기"):
                pw = STUDENT_INFO.get(name, "0000")
                # A열~S열 순서 (총 19개 항목)
                new_row = [
                    str(date), name, level, hw, att, v_t, v_1, v_2, l_1, 0,
                    r_con, r_p, g_con, g_p, reading_voca, reading_sent, writing_feedback, comment, pw
                ]
                sheet.append_row(new_row)
                st.success(f"🎉 {name}({level}) 저장 완료!")

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
                st.success(f"✅ {name_in} 학생의 리포트입니다.")
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인"):
                        st.markdown("#### 📊 학습 현황")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("과제", row['과제 여부'])
                        col2.metric("출결", row['출결'])
                        
                        v_total = int(row['단어 전체 문항']) if row['단어 전체 문항'] else 0
                        v_1 = int(row['단어 1차 맞은 개수']) if row['단어 1차 맞은 개수'] else 0
                        v_2 = int(row['단어 2차 맞은 개수']) if row['단어 2차 맞은 개수'] else 0
                        
                        # 중등 100점 환산 로직
                        if row['구분'] == "중등" and v_total > 0:
                            v_score = round((v_1 / v_total) * 100)
                            v_delta = f"{v_1}/{v_total}"
                            if v_2 > 0: v_delta += f" (2차:{v_2})"
                            col3.metric("단어 점수", f"{v_score}점", v_delta)
                        else:
                            v_val = f"{v_1}/{v_total}"
                            if v_2 > 0: v_val += f" (2차:{v_2})"
                            col3.metric("단어", v_val)
                            
                        col4.metric("듣기", f"{row['듣기 1차 점수']}점")
                        
                        st.markdown("---")
                        st.write(f"**📚 리딩 단어:** {row['리딩 단어']}")
                        st.write(f"**✍️ 리딩 영작/해석:** {row['리딩 지문 영작 및 해석']}")
                        st.info(f"**📝 라이팅 피드백:**\n\n{row['영어홀릭 라이팅']}")
                        st.warning(f"📝 **종합 소견:** {row['코멘트']}")
                
                # --- [사고모델 기반 최종 상담 버튼] ---
                st.divider()
                st.markdown(
                    f"""
                    <a href="kakaotalk://friend/add/sue1984808" style="text-decoration: none;">
                        <div style="display: flex; align-items: center; justify-content: center; background-color: #FEE500; color: #191919; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/KakaoTalk_logo.svg" width="25" style="margin-right: 12px;">
                            원장님과 1:1 상담하기
                        </div>
                    </a>
                    <p style="text-align:center; font-size: 12px; color: #666; margin-top: 10px;">
                        * 모바일에서 클릭 시 원장님 프로필로 즉시 연결됩니다.
                    </p>
                    """, unsafe_allow_html=True
                )
                
            else: st.error("정보가 일치하지 않습니다.")
        except Exception as e: 
            st.error(f"오류 발생: {e}")