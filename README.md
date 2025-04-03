# 교사 연수 추천 챗봇

교사들을 위한 맞춤형 연수 추천 챗봇입니다. 교사들의 관심 분야, 경력, 현재 담당 과목 등을 고려하여 개인화된 연수 추천을 제공합니다.

## 주요 기능

- 관심 분야 다중 선택
- 교직 경력 입력
- 현재 담당 과목/학년 입력
- AI 기반 맞춤형 연수 추천
- 연수별 기대효과 제공
- 추가 관심 분야 추천

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. OpenAI API 키 설정:
- Streamlit secrets.toml 파일을 생성하고 OpenAI API 키를 추가합니다.
- `.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

## 실행 방법

다음 명령어로 애플리케이션을 실행합니다:
```bash
streamlit run app.py
```

## 사용 방법

1. 관심 있는 교육 분야를 선택합니다 (여러 개 선택 가능)
2. 교직 경력을 입력합니다
3. 현재 담당하고 있는 학년/과목을 입력합니다
4. "연수 추천 받기" 버튼을 클릭합니다
5. AI가 제공하는 맞춤형 연수 추천을 확인합니다

## 기술 스택

- Streamlit
- OpenAI API (GPT-3.5-turbo)
- Python 3.8+

## 라이선스

MIT License 