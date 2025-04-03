import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# OpenAI API 키 설정
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("OpenAI API 키가 설정되지 않았습니다. Streamlit Cloud의 Secrets 설정에서 API 키를 추가해주세요.")
        st.stop()
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"OpenAI API 키 설정 중 오류가 발생했습니다: {str(e)}")
    st.error("Streamlit Cloud의 Secrets 설정에서 API 키를 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="교사 맞춤형 연수 추천 시스템",
    page_icon="👩‍🏫", # 따뜻한 느낌의 아이콘으로 변경
    layout="wide"
)

# CSS 스타일 추가 (따뜻한 테마)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');
    body {
        font-family: 'Nanum Gothic', sans-serif;
    }
    .main-header {
        font-size: 2.5rem;
        color: #D97706; /* 따뜻한 주황색 */
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #F59E0B; /* 밝은 주황색 */
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #FDE68A; /* 부드러운 노란색 밑줄 */
        padding-bottom: 0.5rem;
    }
    .card {
        background-color: #FFFBEB; /* 매우 연한 노란색 배경 */
        padding: 1.5rem;
        border-radius: 0.75rem; /* 좀 더 둥근 모서리 */
        margin-bottom: 1.5rem;
        border: 1px solid #FDE68A; /* 부드러운 노란색 테두리 */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .highlight {
        background-color: #FEF3C7; /* 연한 노란색 강조 배경 */
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        color: #92400E; /* 진한 갈색 텍스트 */
        display: inline-block;
        margin-top: 0.5rem;
    }
    /* 사이드바 스타일 */
    .stSidebar > div:first-child {
        background-color: #FFFBEB; /* 카드와 유사한 배경 */
    }
    .stButton>button {
        background-color: #D97706;
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #B45309;
        color: white;
    }
    /* 챗봇 메시지 스타일 */
    .user-message {
        background-color: #FEF3C7; /* 사용자 메시지 배경 */
        padding: 10px;
        border-radius: 10px 10px 0 10px; /* 말풍선 모양 */
        margin-bottom: 10px;
        text-align: right;
        margin-left: auto;
        max-width: 70%;
        border: 1px solid #FDE68A;
    }
    .assistant-message {
        background-color: #FFF7ED; /* 챗봇 메시지 배경 */
        padding: 10px;
        border-radius: 10px 10px 10px 0; /* 말풍선 모양 */
        margin-bottom: 10px;
        text-align: left;
        max-width: 70%;
        border: 1px solid #FDE68A;
    }
</style>
""", unsafe_allow_html=True)

# 앱 제목 설정
st.markdown("<h1 class='main-header'>교사 맞춤형 연수 추천 👩‍🏫</h1>", unsafe_allow_html=True)
st.markdown("선생님의 성장 여정에 따뜻한 등불이 될 연수를 찾아드릴게요.")

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recommendations_made' not in st.session_state:
    st.session_state.recommendations_made = False
if 'recommended_courses' not in st.session_state:
    st.session_state.recommended_courses = []

# 사이드바 구성
with st.sidebar:
    st.header("🔍 프로필 설정")

    teacher_name = st.text_input("이름 (선택사항)")
    teaching_experience = st.slider("교직 경력 (년)", 0, 40, 5)
    school_level = st.selectbox("학교급", ["초등학교", "중학교", "고등학교", "특수학교", "기타"])
    subject = st.text_input("담당 과목 (구체적으로, 예: 중학교 2학년 수학)")

    st.subheader("💡 관심 분야 (복수 선택 가능)")
    categories = {
        "교수학습 혁신": ["AI 기반 맞춤형 교육", "프로젝트 기반 학습(PBL)", "하브루타/토론 수업", "게이미피케이션 활용", "학습자 주도성 신장"],
        "디지털 역량 강화": ["디지털 시민성 교육", "AI 리터러시 및 윤리", "코딩/SW 교육 심화", "데이터 기반 학습 분석", "메타버스 교육 활용"],
        "학생 성장 지원": ["정서행동 위기학생 지원", "회복적 생활교육", "학부모 상담 전문성", "진로 설계 및 코칭", "다문화 학생 이해"],
        "미래 교육 대비": ["기후위기/환경생태 교육", "미래사회 변화와 교육", "에듀테크 동향 및 활용", "교육과정 디자인", "IB 프로그램 이해"],
        "교사 전문성 신장": ["교육 연구 방법론", "전문적 학습공동체 운영", "교사 리더십 개발", "교사 소진 예방 및 힐링", "교육 정책 이해"]
    }

    selected_interests = []
    for category, options in categories.items():
        expander = st.expander(f"**{category}**")
        with expander:
            for option in options:
                if st.checkbox(option, key=f"cb_{option}"):
                    selected_interests.append(option)

    st.markdown("---")

    preference = st.radio("선호 연수 형태", ["온라인", "오프라인", "혼합형", "실시간 온라인", "비실시간 온라인"], horizontal=True)
    time_preference = st.multiselect("선호 연수 시간", ["평일 오전", "평일 오후", "평일 저녁", "주말", "방학 중 집중"])

    recommend_btn = st.button("✨ 맞춤 연수 추천받기")

# 메인 영역 레이아웃
col1, col2 = st.columns([3, 2]) # 추천 영역을 조금 더 넓게

# 연수 추천 영역
with col1:
    if recommend_btn and selected_interests:
        st.markdown("<h2 class='sub-header'>선생님을 위한 맞춤 연수 제안</h2>", unsafe_allow_html=True)

        with st.spinner("⏳ 선생님의 성장을 위한 최적의 연수를 찾고 있어요..."):
            current_date = datetime.now().strftime("%Y년 %m월")
            prompt = f"""
            당신은 대한민국 교육 현장에 대한 이해가 깊고, 교사들의 전문성 개발을 돕는 데 열정적인 교육 컨설턴트입니다.
            다음은 연수 추천을 요청한 교사의 정보입니다:

            - 이름: {teacher_name if teacher_name else "익명"}
            - 교직 경력: {teaching_experience}년차
            - 학교급: {school_level}
            - 담당 과목/학년: {subject if subject else "미입력"}
            - 주요 관심 분야: {', '.join(selected_interests)}
            - 선호 연수 형태: {preference}
            - 선호 연수 시간: {', '.join(time_preference) if time_preference else "미입력"}
            - 현재 시점: {current_date}

            **요청사항:**
            위 교사의 정보(특히 경력, 학교급, 담당과목, 관심분야)를 면밀히 분석하여, 실제 교육 현장에서 즉시 적용 가능하고 교사의 전문성 성장에 실질적인 도움을 줄 수 있는 연수 3가지를 추천해주세요.
            추천 시 다음 사항을 반드시 고려하고, 결과는 아래 지정된 JSON 형식으로만 답변해주세요. 다른 설명은 절대 추가하지 마세요.

            **고려사항:**
            1.  **실질적 도움:** 연수 내용이 교사의 현재 담당 업무나 관심 분야와 어떻게 직접적으로 연결되는지, 어떤 교육적 효과를 기대할 수 있는지 명확히 제시해야 합니다.
            2.  **현장 적용성:** 배운 내용을 교실 수업, 학생 지도, 동료 교사와의 협업 등에 구체적으로 어떻게 적용할 수 있는지 실용적인 팁이나 아이디어를 포함해야 합니다.
            3.  **성장 단계 고려:** 교사의 경력(저경력/중견/고경력)과 학교급에 맞는 연수 내용과 깊이를 고려하여 추천해야 합니다. 예를 들어, 저경력 교사에게는 기본적인 교수법이나 학급 운영 연수가, 고경력 교사에게는 연구나 리더십 관련 연수가 더 적합할 수 있습니다.
            4.  **최신 동향 반영:** AI 교육, 디지털 전환, 기후위기 등 최신 교육 트렌드와 정책 방향을 반영한 연수를 우선적으로 고려해주세요 (교사의 관심사와 부합할 경우).
            5.  **구체적인 연수명:** 실제 교육청, 연수원, 대학 등에서 운영할 법한 현실적이고 구체적인 연수 제목을 사용해주세요. (예: "AI 디지털 교과서 활용 수업 디자인 실습", "PBL 기반 학생 참여형 수업 전문가 과정")

            **JSON 출력 형식:**
            {{
                "recommended_courses": [
                    {{
                        "title": "구체적인 연수 제목",
                        "category": "연수 카테고리 (예: 교수학습 혁신, 디지털 역량)",
                        "target_audience": "{school_level} {subject if subject else ''} 교사, {teaching_experience}년차 내외 교사 등 구체적 대상 명시",
                        "format": "{preference} 또는 추천 형태 (예: 온라인, 혼합형)",
                        "duration": "연수 기간 (예: 3일, 15시간)",
                        "credits": "이수 학점 (예: 1학점)",
                        "description": "연수의 핵심 내용을 요약 설명",
                        "benefits": "이 연수를 통해 교사가 얻을 수 있는 구체적인 성장 지점이나 교육적 효과",
                        "recommendation_reason": "이 교사의 프로필(경력, 관심사 등)과 연관지어 이 연수를 추천하는 구체적인 이유",
                        "practical_application": "배운 내용을 학교 현장에서 실제 수업이나 학생 지도에 적용할 수 있는 구체적인 방법이나 아이디어 2-3가지"
                    }},
                    // ... (총 3개 추천)
                ]
            }}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # 최신 모델 사용 권장
                    messages=[{"role": "system", "content": prompt}],
                    response_format={ "type": "json_object" } # JSON 형식 지정
                )

                recommendations_data = json.loads(response.choices[0].message.content)
                st.session_state.recommended_courses = recommendations_data.get("recommended_courses", [])
                st.session_state.recommendations_made = True

                if not st.session_state.recommended_courses:
                    st.warning("추천 연수를 생성하는 데 실패했습니다. 프로필 설정을 확인하고 다시 시도해주세요.")
                else:
                    for i, course in enumerate(st.session_state.recommended_courses):
                        with st.container():
                            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                            st.markdown(f"### {i+1}. {course.get('title', '제목 없음')}")
                            st.caption(f"🎯 추천 대상: {course.get('target_audience', '정보 없음')}")
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.markdown(f"**카테고리:** {course.get('category', '-')}")
                            with col_b:
                                st.markdown(f"**형태:** {course.get('format', '-')}")
                            with col_c:
                                st.markdown(f"**학점:** {course.get('credits', '-')}")

                            st.markdown(f"**📅 기간:** {course.get('duration', '-')}")
                            st.markdown(f"**📝 내용:** {course.get('description', '-')}")
                            st.markdown(f"<div class='highlight'>📈 기대 효과: {course.get('benefits', '-')}</div>",
                                       unsafe_allow_html=True)
                            st.markdown(f"**💡 추천 이유:** {course.get('recommendation_reason', '-')}")
                            st.markdown(f"**🚀 현장 적용 Tip:** {course.get('practical_application', '-')}")
                            st.markdown("</div>", unsafe_allow_html=True)

            except json.JSONDecodeError:
                 st.error("🤖 추천 결과를 분석하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                 st.session_state.recommendations_made = False
            except Exception as e:
                 st.error(f"🤖 오류가 발생했습니다: {str(e)}")
                 st.error("다시 시도해주세요.")
                 st.session_state.recommendations_made = False

    elif recommend_btn and not selected_interests:
        st.warning("⚠️ 하나 이상의 관심 분야를 선택해주세요!")

# 챗봇 인터페이스
with col2:
    st.markdown("<h2 class='sub-header'>💬 연수 상담 챗봇</h2>", unsafe_allow_html=True)
    if not st.session_state.recommendations_made:
        st.info("먼저 프로필을 설정하고 연수 추천을 받아보세요. 추천 결과에 대해 궁금한 점을 질문할 수 있습니다.")
    else:
        st.success("연수 추천 결과에 대해 궁금한 점이나 추가 정보가 필요하시면 아래에 질문해주세요!")

    # 채팅 이력 표시
    chat_container = st.container(height=500) # 채팅 영역 높이 지정
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'><strong>나:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'><strong>챗봇:</strong> {message['content']}</div>", unsafe_allow_html=True)

    # 사용자 입력
    user_question = st.chat_input("연수에 대해 질문해보세요...") # chat_input 사용

    if user_question:
        # 사용자 메시지 저장 및 표시
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with chat_container:
             st.markdown(f"<div class='user-message'><strong>나:</strong> {user_question}</div>", unsafe_allow_html=True)

        # 챗봇 응답 생성
        interests_text = ', '.join(selected_interests) if selected_interests else '미선택'
        recommended_courses_summary = "\n".join([f"- {c.get('title', '')}: {c.get('description', '')}" for c in st.session_state.recommended_courses]) if st.session_state.recommended_courses else "아직 추천된 연수 없음"

        chat_prompt = f"""
        당신은 '따뜻한 연수 도우미' 챗봇입니다. 교사의 성장을 진심으로 응원하며, 친절하고 상세하게 답변해야 합니다.

        **교사 정보:**
        - 이름: {teacher_name if teacher_name else "익명"}
        - 경력: {teaching_experience}년차
        - 학교급: {school_level}
        - 담당: {subject if subject else "미입력"}
        - 관심 분야: {interests_text}
        - 선호 형태/시간: {preference} / {', '.join(time_preference) if time_preference else "미입력"}

        **현재 추천된 연수 목록 (참고용):**
        {recommended_courses_summary}

        **챗봇의 역할:**
        1.  교사의 질문 의도를 파악하고, 위 교사 정보와 추천된 연수 목록을 바탕으로 **매우 구체적이고 실용적인 답변**을 제공합니다.
        2.  추천된 연수에 대한 **심층 질문**(예: 특정 연수의 실제 후기, 유사 연수 비교, 연수 내용의 현장 적용 방안 심화)에 상세히 답변합니다.
        3.  추천 목록 외에 **새로운 연수 정보를 질문**하면, 교사의 프로필에 맞춰 관련성 높은 정보를 탐색하여 안내합니다 (실제 검색 기능은 없으므로, 그럴듯한 정보를 생성).
        4.  연수 이수 후의 **성장 경로**나 **역량 개발**에 대한 조언을 제공합니다.
        5.  **따뜻하고 공감하는 어조**를 사용하며, 교사의 노고를 격려하는 메시지를 포함합니다.
        6.  답변은 명확하고 이해하기 쉽게, 필요시 **불렛 포인트나 단계별 설명**을 활용합니다.
        7.  정보가 부족하거나 확실하지 않을 때는 솔직하게 인정하고, 추가 정보를 찾을 수 있는 방법을 안내합니다.

        **교사의 질문:** {user_question}

        **답변:**
        """

        try:
            with st.spinner("답변을 생각하고 있어요..."):
                chat_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": chat_prompt},
                        # 이전 대화 내용을 포함시켜 문맥 유지 (선택 사항)
                        # *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history[-5:]], # 최근 5개 대화
                        {"role": "user", "content": user_question}
                    ]
                )
                assistant_response = chat_response.choices[0].message.content

                # 챗봇 응답 저장 및 표시
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                with chat_container:
                    st.markdown(f"<div class='assistant-message'><strong>챗봇:</strong> {assistant_response}</div>", unsafe_allow_html=True)
                # 입력 필드 초기화를 위해 rerun 대신 chat_input 자체 기능 활용

        except Exception as e:
            st.error(f"🤖 답변 생성 중 오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #A1A1AA; font-size: 0.8rem;">
    © 2025 교사 맞춤형 연수 추천 시스템 | ♥️선생님의 빛나는 성장을 응원합니다 ✨ Made by 김문정
</div>
""", unsafe_allow_html=True)
