import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- [1. 앱 설정] ---
st.set_page_config(page_title="쑤샘영어 스마트 리포트", page_icon="🎓", layout="wide")

st.markdown("""
    <div style="background: linear-gradient(to right, #0f172a, #1e293b, #0f172a); 
                padding: 30px; border-radius: 15px; border: 2px solid #38bdf8; 
                text-align: center; box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.3);">
        <h1 style="color: #facc15; margin-bottom: 5px; font-family: 'Pretendard', sans-serif;">
            🎓 쑤샘영어 SMART REPORT
        </h1>
        <p style="color: #38bdf8; font-size: 1.1rem; margin-top: 0;">SUE ENGLISH INNOVATION SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)
st.write("") 

# --- [2. 학생 정보 DB] ---
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
    st.error(f"연결 오류: {e}")
    connection_success = False

menu = st.sidebar.selectbox("메뉴 선택", ["학부모 조회용", "선생님 입력용"])

# --- [선생님 입력용 로직] ---
if menu == "선생님 입력용":
    st.title("🎓 성적 입력 시스템")
    if st.sidebar.text_input("관리자 비밀번호", type="password") == "1234":
        name = st.selectbox("👤 학생 선택", STUDENT_LIST)
        
        # [해결 포인트] 구분을 폼 밖으로 꺼내서 듣기 입력창이 즉시 바뀌게 합니다.
        level = st.radio("🏫 학교급 구분", ["초등", "중등"], horizontal=True)
        
        with st.form("input_form", clear_on_submit=True):
            date = st.date_input("📅 평가 날짜", datetime.now())
            hw = st.radio("📚 과제 여부", ["완료", "미흡", "미완료"], horizontal=True)
            att = st.radio("✅ 출결 상태", ["양호", "지각", "결석"], horizontal=True)
            
            # --- 섹션 1: 단어 & 듣기 ---
            st.markdown("### 📊 단어 & 듣기")
            v_t = st.number_input("단어 전체 문항", value=60)
            col1, col2 = st.columns(2)
            with col1: v_1 = st.number_input("단어 1차 맞은 개수", 0)
            with col2: v_2 = st.number_input("단어 2차 맞은 개수", 0)
            
            if level == "중등":
                lc1, lc2 = st.columns(2)
                with lc1: l_total = st.number_input("듣기 전체 문항", value=20)
                with lc2: l_correct = st.number_input("듣기 맞은 개수", 0)
                l_score = 0 # 폼 제출 시 자동 계산
            else:
                l_score = st.number_input("듣기 점수 (초등)", 0, 100)
                l_total, l_correct = 1, 0 # 계산 에러 방지용

            # --- 섹션 2: 리딩 ---
            st.markdown("---")
            st.markdown("### 📖 리딩")
            r_con = st.text_input("리딩 수업 내용 (없으면 비움)")
            r_p = st.selectbox("리딩 수행도", ["-", "우수", "보통", "노력요함"])
            reading_voca = st.selectbox("📚 리딩 단어 암기", ["-", "열심히 외움", "대충 외움", "노력 필요"])
            reading_sent = st.selectbox("✍️ 리딩 지문 영작/해석", ["-", "열심히 했음", "조금 더 공부하기", "노력 필요"])
            
            # --- 섹션 3: 문법 ---
            st.markdown("---")
            st.markdown("### ✍️ 문법")
            g_con = st.text_input("문법 수업 내용 (없으면 비움)")
            g_p = st.selectbox("문법 수행도", ["-", "우수", "보통", "노력요함"])

            # --- 섹션 4: 영어홀릭 라이팅 ---
            st.markdown("---")
            st.markdown("### ✒️ 영어홀릭 라이팅")
            writing_feedback = st.text_area("라이팅 피드백")

            # --- 섹션 5: 종합 소견 ---
            st.markdown("---")
            st.markdown("### 🌟 선생님 종합 소견")
            comment = st.text_area("선생님 코멘트")

            if st.form_submit_button("리포트 저장하기"):
                # 점수 환산 로직 (100점 만점)
                if level == "중등":
                    l_score = round((l_correct / l_total) * 100) if l_total > 0 else 0
                
                pw = STUDENT_INFO.get(name, "0000")
                new_row = [str(date), name, level, hw, att, v_t, v_1, v_2, l_score, 0, r_con, r_p, g_con, g_p, reading_voca, reading_sent, writing_feedback, comment, pw]
                sheet.append_row(new_row)
                st.success(f"🎉 {name}({level}) 리포트 저장 완료!")

# --- [학부모 조회용 로직] ---
elif menu == "학부모 조회용":
    st.title("🔍 우리 아이 스마트 리포트")
    c1, c2 = st.columns(2)
    with c1: name_in = st.text_input("👤 학생 이름")
    with c2: pw_in = st.text_input("🔑 비밀번호", type="password")
    
    if name_in and pw_in and connection_success:
        try:
            all_v = sheet.get_all_values()
            df = pd.DataFrame(all_v[1:], columns=all_v[0])
            res = df[(df['학생 이름'] == name_in) & (df['비밀번호'].astype(str).str.strip() == str(p_in).strip())]
            
            if not res.empty:
                for _, row in res.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['평가 날짜']} 리포트 확인"):
                        # --- 1. 단어 & 듣기 ---
                        st.markdown("#### 📊 단어 & 듣기")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("과제", row['과제 여부'])
                        m2.metric("출결", row['출결'])
                        
                        vt = int(row['단어 전체 문항']) if row['단어 전체 문항'] else 0
                        v1 = int(row['단어 1차 맞은 개수']) if row['단어 1차 맞은 개수'] else 0
                        v2 = int(row['단어 2차 맞은 개수']) if row['단어 2차 맞은 개수'] else 0
                        v_score = round((v1/vt)*100) if vt > 0 else 0
                        v_desc = f"{v1}/{vt}" + (f" (2차:{v2})" if v2 > 0 else "")
                        m3.metric("단어 점수", f"{v_score}점", v_desc)
                        m4.metric("듣기 점수", f"{row['듣기 1차 점수']}점")
                        
                        # --- 2. 리딩 ---
                        if row['리딩 수업 내용'] or row['리딩 단어'] != "-" or row['리딩 지문 영작 및 해석'] != "-":
                            st.markdown("---")
                            st.markdown("#### 📖 리딩")
                            if row['리딩 수업 내용']: st.write(f"**학습 내용:** {row['리딩 수업 내용']}")
                            if row['리딩 단어'] != "-": st.write(f"**단어 암기:** {row['리딩 단어']}")
                            if row['리딩 지문 영작 및 해석'] != "-": st.write(f"**영작/해석:** {row['리딩 지문 영작 및 해석']}")
                            if row['리딩 수행도'] != "-": st.write(f"**수행도:** {row['리딩 수행도']}")

                        # --- 3. 문법 ---
                        if row['문법 수업 내용'] or row['문법 수행도'] != "-":
                            st.markdown("---")
                            st.markdown("#### ✍️ 문법")
                            if row['문법 수업 내용']: st.write(f"**학습 내용:** {row['문법 수업 내용']}")
                            if row['문법 수행도'] != "-": st.write(f"**수행도:** {row['문법 수행도']}")

                        # --- 4. 영어홀릭 라이팅 ---
                        if row['영어홀릭 라이팅']:
                            st.markdown("---")
                            st.markdown("#### ✒️ 영어홀릭 라이팅")
                            st.info(row['영어홀릭 라이팅'])

                        # --- 5. 종합 소견 ---
                        st.markdown("---")
                        st.warning(f"🌟 **선생님 소견:** {row['코멘트']}")
                st.divider()
                st.markdown("<div style='background-color:#FEE500; padding:15px; border-radius:10px; color:black; font-weight:bold; text-align:center;'>리포트 보시고 궁금하신 점은 카톡주세요! 😊</div>", unsafe_allow_html=True)
            else: st.error("정보가 일치하지 않습니다.")
        except Exception as e: st.error(f"오류: {e}")