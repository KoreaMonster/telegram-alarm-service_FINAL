#텔레그램 채널에서 메시지를 스크래핑하고 키워드를 검색하는 기능

# from src.main import keyword
from app.core.telegram_client import client

# from telegram_client import client



#
# async def search_channels_by_keyword (message):                  #키워드를 포한하는 메세지 검색
#     matching_messages = []
#
#     if message and keyword.lower() in message.text.lower():
#         matching_messages.append((message.sender_id, message.text))  # 메시지 추가
#         print(f"matching_messages를 추가했습니다.")
#         print(f"{message.sender_id}\n{message.text}")
#
#     return matching_messages
#

# @client.on(events.NewMessage(incoming=True))  # incoming=True로 수신된 메시지만 처리
# async def handler(event):
#     """
#     새로운 수신 메시지가 도착했을 때 호출되는 이벤트 핸들러.
#     :param event: 새로 수신된 메시지 이벤트
#     """
#     matching_messages = []
#
#     message = event.message  # 수신된 메시지 객체
#
#     if message_has_keyword(message.text):
#         matching_messages.append(message)  # message 객체 추가
#         print(f"{message: 10f} | 메세지가 추가되었습니다.")

channel_message_map = {}    #딕셔너리: 키-리스트


async def recent_10_messages(channels, keyword):
    """
    채널들에서 최근 10개 메시지를 가져와서 키워드가 포함된 메시지를 찾는 함수

    Args:
        channels: 채널 사용자명 또는 ID 목록
        keyword: 찾을 키워드

    Returns:
        dict: 채널별로 키워드가 포함된 메시지 목록
    """
    channel_message_map = {}

    # channels가 문자열이면 리스트로 변환
    if isinstance(channels, str):
        channels = [channels]

    for channel in channels:
        try:
            channel_entity = await client.get_entity(channel)
            messages = []

            async for message in client.iter_messages(channel_entity, limit=10):
                if message.text:
                    messages.append(message.text)

            channel_message_map[channel_entity.title] = messages
            # newest -> late로 저장됨

        except Exception as e:
            print(f"채널 {channel} 처리 중 오류: {str(e)}")
            continue

    # 키워드 매칭 결과 저장
    matching_results = {}

    for channel_title, message_list in channel_message_map.items():
        matching_messages = message_has_keyword(keyword, channel_title, message_list)
        if matching_messages:  # 매칭된 메시지가 있는 경우만 저장
            matching_results[channel_title] = matching_messages

    return matching_results


def message_has_keyword(keyword, channel_title, message_lst: list):
    """
    메시지 목록에서 키워드가 완전히 매칭되는 메시지를 찾는 함수
    (split() 함수를 사용하여 단어 분리)

    Args:
        keyword: 검색할 키워드
        channel_title: 채널 제목
        message_lst: 메시지 목록

    Returns:
        list: 키워드가 독립적인 단어로 포함된 메시지 목록
    """
    matching_messages = []
    keyword_lower = keyword.lower()

    for message in message_lst:
        # 공백을 기준으로 단어 분리
        words = message.lower().split()

        # 각 단어가 정확히 키워드와 일치하는지 확인
        if keyword_lower in words:
            matching_messages.append(message)

    return matching_messages


def display_keyword_search_results(matching_results, keyword):
    """
    키워드 검색 결과를 예쁘게 출력하는 함수

    Args:
        matching_results (dict): 채널별 매칭된 메시지 딕셔너리
        keyword (str): 검색한 키워드
    """
    print(f"\n\n===== '{keyword}' 키워드 검색 결과 =====")

    if not matching_results:
        print(f"❌ '{keyword}' 키워드가 포함된 메시지를 찾을 수 없습니다.")
        return

    total_channels = len(matching_results)
    total_messages = sum(len(messages) for messages in matching_results.values())

    print(f"📊 요약: {total_channels}개 채널에서 {total_messages}개의 메시지를 발견했습니다.")
    print("=" * 60)

    for channel_idx, (channel_title, messages) in enumerate(matching_results.items(), 1):
        print(f"\n🔍 [{channel_idx}] {channel_title}")
        print(f"📈 매칭된 메시지: {len(messages)}개")
        print("-" * 50)

        for msg_idx, message in enumerate(messages, 1):
            # 메시지에서 키워드 하이라이트
            highlighted_message = highlight_keyword(message, keyword)

            # 메시지가 너무 길면 적절히 줄바꿈
            formatted_message = format_long_message(highlighted_message, max_length=80)

            print(f"\n  💬 메시지 {msg_idx}:")
            print(f"  {formatted_message}")
            print("  " + "·" * 40)

        print("-" * 50)


def highlight_keyword(message, keyword):
    """
    메시지에서 키워드를 하이라이트하는 함수

    Args:
        message (str): 원본 메시지
        keyword (str): 하이라이트할 키워드

    Returns:
        str: 키워드가 하이라이트된 메시지
    """
    import re

    # 대소문자 구분 없이 키워드 찾기
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    # 키워드를 ⭐[키워드]⭐로 하이라이트
    highlighted = pattern.sub(f"⭐{keyword.upper()}⭐", message)

    return highlighted


def format_long_message(message, max_length=80):
    """
    긴 메시지를 적절히 줄바꿈하는 함수

    Args:
        message (str): 원본 메시지
        max_length (int): 한 줄 최대 길이

    Returns:
        str: 포맷된 메시지
    """
    if len(message) <= max_length:
        return message

    words = message.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)

        if current_length + word_length + 1 <= max_length:
            current_line.append(word)
            current_length += word_length + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                # 단어 자체가 너무 긴 경우
                lines.append(word[:max_length] + "...")
                current_line = []
                current_length = 0

    if current_line:
        lines.append(" ".join(current_line))

    return "\n  ".join(lines)


def display_keyword_search_summary(matching_results, keyword):
    """
    키워드 검색 결과의 간단한 요약만 출력하는 함수

    Args:
        matching_results (dict): 채널별 매칭된 메시지 딕셔너리
        keyword (str): 검색한 키워드
    """
    print(f"\n===== '{keyword}' 키워드 검색 요약 =====")

    if not matching_results:
        print(f"❌ '{keyword}' 키워드가 포함된 메시지를 찾을 수 없습니다.")
        return

    for channel_title, messages in matching_results.items():
        print(f"📍 {channel_title}: {len(messages)}개 메시지")