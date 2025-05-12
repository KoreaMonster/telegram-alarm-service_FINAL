#보안뉴스 RSS, 데일리 시큐 RSS
#키워드 추출, 중복 제거, AI기반 재구성(이건 나중에)
import os

import genai
from google import genai
from google.genai import types

import feedparser
import requests

from src.config import GEMINI_API_KEY


def get_boannews_titles(rss_url='http://www.boannews.com/media/news_rss.xml?mkind=1', max_items=10):

    feed = feedparser.parse(rss_url)
    titles = [entry.title for entry in feed.entries[:max_items]]

    return titles

def get_dailysecu_titles(rss_url='https://www.dailysecu.com/rss/S1N2.xml', max_items=10):

    feed = feedparser.parse(rss_url)
    titles = [entry.title for entry in feed.entries[:max_items]]

    return titles

def generate_prompt(titles: list) -> str:
    prompt = (
        "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
        + "\nThese are 20 recent news headlines related to cybersecurity.Based on them, extract English keywords that are likely to appear in the usernames of Telegram channels posing security threats and trends. Each keyword must be a single word. Return the result as a Python list: ['keyword1', 'keyword2', ..., 'keyword6']."
    )
    return prompt

def get_keywords_from_gemini(titles):
    # Gemini API 클라이언트 초기화
    client = genai.Client(
        api_key=GEMINI_API_KEY,  # 환경 변수에서 가져오지 말고 직접 값 사용
    )

    # 프롬프트 생성 (기존 함수의 방식대로)
    prompt = generate_prompt(titles)

    # 모델 및 컨텐츠 설정
    model = "gemini-2.0-flash-lite"  # 복사된 함수에서 사용하는 모델

    # 컨텐츠 설정
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    # 생성 설정
    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.8,
        max_output_tokens=2400,
        response_mime_type="text/plain",
    )

    try:
        # API 요청 (스트림 방식 대신 일반 응답 방식 사용)
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        # 응답 파싱
        if response and hasattr(response, 'text'):
            text_response = response.text

            # 파이썬 리스트 형식의 텍스트 추출 시도
            import re
            list_pattern = r'\[.*?\]'
            list_match = re.search(list_pattern, text_response, re.DOTALL)

            if list_match:
                # 리스트 형식의 텍스트를 찾았을 경우 파싱
                list_text = list_match.group(0)

                try:
                    # 문자열을 실제 리스트로 변환 시도
                    keywords = eval(list_text)
                    # 최대 10개 키워드 반환
                    return keywords[:10]
                except:
                    # eval 실패 시 수동 파싱
                    # 대괄호 제거 및 쉼표로 분리
                    list_text = list_text.strip('[]')
                    keywords = [k.strip().strip('\'"') for k in list_text.split(',')]
                    # 빈 항목 및 따옴표 제거
                    keywords = [k for k in keywords if k]
                    return keywords[:10]

            # 리스트 형식이 없으면 줄바꿈으로 구분된 텍스트 추출
            lines = text_response.strip().split('\n')
            keywords = []

            for line in lines:
                clean_line = line.strip()
                # 코드 블록 마커 제거
                if clean_line in ['```', '```python']:
                    continue

                # 일반 텍스트 라인에서 키워드 추출
                if clean_line and not clean_line.startswith(
                        ('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    # 앞에 숫자와 점이 있으면 제거
                    if '. ' in clean_line and clean_line[0].isdigit():
                        clean_line = clean_line.split('. ', 1)[1]
                    # 따옴표, 대괄호 등 제거
                    clean_line = clean_line.strip('\'"[]')
                    if clean_line:
                        keywords.append(clean_line)

            # 결과 출력 및 반환
            print("추출된 키워드:")
            print(keywords)
            return keywords[:10]

        # 응답 형식이 예상과 다를 경우
        print("API 응답 형식이 예상과 다릅니다:", response)
        return []

    except Exception as e:
        print(f"Gemini API 요청 중 오류 발생: {str(e)}")
        return []
    # prompt = generate_prompt(titles)
    #
    # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    # headers = {'Content-Type': 'application/json'}
    #
    # payload = {
    #     "contents": [{
    #         "parts": [{"text": prompt}]
    #     }]
    # }
    #
    # try:
    #     # API 요청 보내기
    #     response = requests.post(url, headers=headers, data=json.dumps(payload))
    #     response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
    #
    #     # 응답 파싱
    #     result = response.json()
    #
    #     # 텍스트 응답 추출
    #     if 'candidates' in result and len(result['candidates']) > 0:
    #         if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
    #             text_response = result['candidates'][0]['content']['parts'][0]['text']
    #
    #             # 키워드만 추출 (마지막 10줄 추출)
    #             lines = text_response.strip().split('\n')
    #             keywords = []
    #
    #             # 응답의 마지막 부분에서 키워드 추출 시도
    #             for line in lines:
    #                 # 숫자, 점, 공백 등을 제거하고 순수 키워드만 추출
    #                 clean_line = line.strip()
    #                 if clean_line and not clean_line.startswith(
    #                         ('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
    #                     # 앞에 숫자와 점이 있으면 제거
    #                     if '. ' in clean_line and clean_line[0].isdigit():
    #                         clean_line = clean_line.split('. ', 1)[1]
    #                     keywords.append(clean_line)
    #
    #             # 키워드가 10개 미만이면 다른 방식으로 추출 시도
    #             if len(keywords) < 10:
    #                 for line in lines:
    #                     clean_line = line.strip()
    #                     # 숫자로 시작하는 라인 찾기
    #                     if clean_line and clean_line[0].isdigit() and '. ' in clean_line:
    #                         keyword = clean_line.split('. ', 1)[1]
    #                         if keyword not in keywords:
    #                             keywords.append(keyword)
    #
    #             # 키워드 목록이 비어있으면 마지막 시도
    #             if not keywords:
    #                 # 가장 단순한 방법: 마지막 부분에서 줄바꿈으로 구분된 텍스트 추출
    #                 last_part = text_response.split('\n\n')[-1]
    #                 keywords = [k.strip() for k in last_part.split('\n') if k.strip()]
    #
    #             # 최대 10개 키워드 반환
    #             print("sdhjn")
    #             print(keywords)
    #             return keywords[:10]
    #
    #     # 응답 형식이 예상과 다를 경우
    #     print("API 응답 형식이 예상과 다릅니다:", result)
    #     return []
    #
    # except requests.exceptions.RequestException as e:
    #     print(f"API 요청 중 오류 발생: {str(e)}")
    #     return []
    # except (KeyError, IndexError, json.JSONDecodeError) as e:
    #     print(f"응답 파싱 중 오류 발생: {str(e)}")
    #     return []