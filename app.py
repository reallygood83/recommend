import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# OpenAI API 키 설정
try:
    # OpenAI API 키 설정
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)  # 직접 import한 방식으로 생성
except Exception as e:
    st.error(f"OpenAI API 키 설정 중 오류가 발생했습니다: {str(e)}")
    st.error("Streamlit Cloud의 Secrets 설정에서 API 키를 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="교사 맞춤형 연수 추천 시스템",
    page_icon="🎓",
    layout="wide"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .highlight {
        background-color: #DBEAFE;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 앱 제목 설정
st.markdown("<h1 class='main-header'>교사 맞춤형 연수 추천 시스템</h1>", unsafe_allow_html=True)
st.markdown("교사 여러분의 관심 분야와 경력에 맞는 최적의 연수를 추천해 드립니다.")

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 사이드바 구성
with st.sidebar:
    st.header("프로필 설정")
    
    # 기본 정보 입력
    teacher_name = st.text_input("이름 (선택사항)")
    teaching_experience = st.slider("교직 경력 (년)", 0, 40, 5)
    school_level = st.selectbox("학교급", ["초등학교", "중학교", "고등학교", "특수학교", "기타"])
    subject = st.text_input("담당 과목 (선택사항)")
    
    st.subheader("관심 분야를 선택해주세요")
    # 관심 분야 카테고리
    categories = {
        "교수학습": ["교수법 혁신", "교육과정 재구성", "학습 평가", "교실 관리", "블렌디드 러닝"],
        "디지털 역량": ["디지털 리터러시", "AI 교육", "메이커 교육", "에듀테크 활용", "온라인 수업 설계"],
        "학생 지도": ["학생 상담", "학교폭력 예방", "진로 지도", "생활지도", "학생 자치"],
        "포용교육": ["특수교육", "다문화 교육", "교육격차 해소", "통합교육", "학습 부진아 지도"],
        "교사 역량": ["교사 리더십", "연구 설계", "전문적 학습공동체", "교사 복지", "교권 보호"]
    }
    
    # 각 카테고리별 체크박스 그룹
    selected_interests = []
    for category, options in categories.items():
        st.markdown(f"**{category}**")
        for option in options:
            if st.checkbox(option, key=f"cb_{option}"):
                selected_interests.append(option)
                
    st.markdown("---")
    
    # 추가 선호사항
    preference = st.radio("선호하는 연수 형태", ["온라인", "오프라인", "혼합형", "상관없음"])
    time_preference = st.multiselect("선호하는 연수 시간대", 
                                     ["평일 오전", "평일 오후", "평일 저녁", "주말"])

    # 연수 추천 버튼
    recommend_btn = st.button("연수 추천 받기", type="primary")

# 메인 영역 레이아웃
col1, col2 = st.columns([2, 1])

# 연수 추천 영역
with col1:
    if recommend_btn and selected_interests:
        st.markdown("<h2 class='sub-header'>맞춤형 연수 추천 결과</h2>", unsafe_allow_html=True)
        
        with st.spinner("연수 정보를 분석하고 있습니다..."):
            # 사용자 입력을 기반으로 프롬프트 생성
            current_date = datetime.now().strftime("%Y년 %m월")
            prompt = f"""
            당신은 교사 맞춤형 연수 추천 전문가입니다. 다음 정보를 바탕으로 교사에게 필요한 연수를 추천해주세요:
            
            이름: {teacher_name if teacher_name else "선생님"}
            관심 분야: {', '.join(selected_interests)}
            교직 경력: {teaching_experience}년
            학교급: {school_level}
            담당 과목: {subject if subject else "미입력"}
            선호하는 연수 형태: {preference}
            선호하는 연수 시간대: {', '.join(time_preference) if time_preference else "미입력"}
            현재 시점: {current_date}
            
            다음 형식의 JSON으로 답변해주세요:
            {{
                "recommended_courses": [
                    {{
                        "title": "연수 제목",
                        "category": "연수 카테고리",
                        "format": "온라인/오프라인/혼합형",
                        "duration": "연수 기간",
                        "credits": "이수 학점",
                        "description": "연수 간략 설명",
                        "benefits": "기대효과",
                        "recommendation_reason": "이 연수를 추천하는 이유"
                    }},
                    ... (총 3개)
                ],
                "related_areas": [
                    {{
                        "area": "관련 분야명",
                        "relevance": "선택한 관심 분야와의 관련성",
                        "benefits": "이 분야를 학습했을 때의 장점"
                    }},
                    ... (총 2개)
                ]
            }}
            
            실제 존재할 것 같은 현실적인 연수 과정을 추천해주세요. 연수 제목은 실제 교육청이나 연수원에서 제공할 법한 구체적인 이름으로 작성해주세요.
            """
            
            try:
                # OpenAI API 호출
                response = client.chat.completions.create(
                    model="gpt-4",  # 또는 사용 가능한 최신 모델
                    messages=[{"role": "system", "content": prompt}]
                )
                
                # 응답 파싱
                recommendations = json.loads(response.choices[0].message.content)
                
                # 추천 연수 분야 표시
                for i, course in enumerate(recommendations["recommended_courses"]):
                    with st.container():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"### {i+1}. {course['title']}")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.markdown(f"**카테고리:** {course['category']}")
                        with col_b:
                            st.markdown(f"**형태:** {course['format']}")
                        with col_c:
                            st.markdown(f"**이수학점:** {course['credits']}")
                        
                        st.markdown(f"**기간:** {course['duration']}")
                        st.markdown(f"**내용:** {course['description']}")
                        st.markdown(f"<div class='highlight'>기대효과: {course['benefits']}</div>", 
                                   unsafe_allow_html=True)
                        st.markdown(f"**추천 이유:** {course['recommendation_reason']}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # 관련 분야 추천
                st.markdown("<h2 class='sub-header'>추가 관심 분야 추천</h2>", unsafe_allow_html=True)
                for i, related in enumerate(recommendations["related_areas"]):
                    with st.container():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        st.markdown(f"### {related['area']}")
                        st.markdown(f"**선택한 분야와의 관련성:** {related['relevance']}")
                        st.markdown(f"**학습 시 장점:** {related['benefits']}")
                        st.markdown("</div>", unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.error("다시 시도해주세요.")
    
    elif recommend_btn and not selected_interests:
        st.warning("최소 하나 이상의 관심 분야를 선택해주세요.")

# 챗봇 인터페이스
with col2:
    st.markdown("<h2 class='sub-header'>연수 상담 챗봇</h2>", unsafe_allow_html=True)
    st.markdown("연수에 관한 질문이 있으시면 아래에 입력해주세요.")
    
    # 채팅 이력 표시
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div style='background-color:#E0F2FE; padding:10px; border-radius:5px; margin-bottom:10px;'>"
                        f"<strong>선생님:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#F0FDF4; padding:10px; border-radius:5px; margin-bottom:10px;'>"
                        f"<strong>연수 도우미:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # 사용자 입력
    user_question = st.text_input("질문을 입력하세요:", key="user_input")
    
    if user_question:
        # 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        # 프롬프트 생성
        interests_text = ', '.join(selected_interests) if selected_interests else '미선택'
        
        chat_prompt = f"""
        당신은 '연수 도우미'라는 이름의 교사 연수 전문가입니다. 다음 정보를 가진 교사에게 친절하고 전문적으로 답변해주세요:
        
        학교급: {school_level}
        교직 경력: {teaching_experience}년
        관심 분야: {interests_text}
        담당 과목: {subject if subject else "미입력"}
        
        답변 시 다음 사항을 지켜주세요:
        1. 실용적이고 구체적인 조언을 제공하세요
        2. 교사의 경력과 관심사에 맞는 맞춤형 정보를 제공하세요
        3. 정확한 정보가 없다면 추측하지 말고 모른다고 솔직하게 말하세요
        4. 간결하고 명확하게 답변하세요 (3-4문장 이내)
        5. 필요하다면 실제 교육부나 교육청의 정책 방향성을 반영하세요
        
        질문: {user_question}
        """
        
        try:
            # OpenAI API 호출
            with st.spinner("답변을 생성하고 있습니다..."):
                chat_response = client.chat.completions.create(
                    model="gpt-4",  # 또는 사용 가능한 최신 모델
                    messages=[{"role": "system", "content": chat_prompt}]
                )
                
                # 응답 저장 및 표시
                assistant_response = chat_response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                
                # 화면 새로고침하여 채팅 이력에 표시
                st.rerun()
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
    © 2025 교사 맞춤형 연수 추천 시스템 | Made 김문정 💕for Teachers.
</div>
""", unsafe_allow_html=True)