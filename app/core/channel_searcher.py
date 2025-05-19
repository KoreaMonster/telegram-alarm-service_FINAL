import json

from telethon.tl.functions.contacts import SearchRequest

from app.core.security_keyword_extractor import get_keywords_from_gemini, get_dailysecu_titles, get_boannews_titles
from app.core.telegram_client import client

fixed_keywords = ["hack", "crack", "leak", "botnet", "exploit", "phishing", "ransomware", "carding", "keylogger", "malware"]

def load_fixed_keyword(file= 'fixed_keyword.json'):
    with open(file, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    return keywords

def save_fixed_keyword(file= 'fixed_keyword.json'):
    with open(file, 'w') as f:
        json.dump(fixed_keywords, f)


def add_fixed_keyword(fixed_keyword: str):
    keyword_exists = False

    for i in range (len(fixed_keywords)):
        if fixed_keywords[i] == fixed_keyword:
            keyword_exists = True
            break
    if keyword_exists == False:
        fixed_keywords.append(fixed_keyword)
        save_fixed_keyword()

        print(f"채널 {fixed_keyword}가 추가되었습니다.")
    else:
        print(f"채널 {fixed_keyword}는 이미 존재합니다.")

def remove_channel_keyword(del_keyword: str):            #리스트에 있는 채널을 삭제하기
    keyword_exists = False
    # combine_channel_keywords = get_combined_keyword()
    # ## 고정값만 할까?
    channel_keywords = load_fixed_keyword()

    for i in range (len(channel_keywords)):
        if channel_keywords[i] == del_keyword:
            keyword_exists = True
            break

    if keyword_exists == True:
        channel_keywords.remove(del_keyword)
        save_fixed_keyword()

        print(f"채널 {del_keyword}가 삭제되었습니다.")
    else:
        print(f"채널 {del_keyword}가 존재하지 않습니다")

def get_dynamic_keyword():
    dynamic_channel_keywords= []

    # print(f"dynamic")
    # print(get_dailysecu_titles() + get_boannews_titles())

    dynamic_channel_keywords = get_keywords_from_gemini(get_dailysecu_titles() + get_boannews_titles())

    return dynamic_channel_keywords



def get_combined_keyword():
    print(f"Fixed{load_fixed_keyword()}")
    print(f"AI Trend{get_dynamic_keyword()}")
    combined_channel_keyword = list(set(get_dynamic_keyword() + load_fixed_keyword()))
    print(f"combined{combined_channel_keyword}")

    return combined_channel_keyword

async def search_public_channels(channel_keywords, max_channel=5, max_age_date=7):
    from telethon.tl.types import Channel

    results_map = {}

    for keyword in channel_keywords:
        # print(f"\n'{keyword}' 검색 중...")

        try:
            search_result = await client(SearchRequest(
                q= keyword,
                limit= max_channel
            ))
            found_channels = []  # 각 키워드별 채널 임시 저장

            # #세부적인 필터링
            # print(search_result)
            # #출력하는 함수 - 필터링

            for chat in search_result.chats:
                if isinstance(chat, Channel):
                    if hasattr(chat, 'username') and chat.username:
                        try:
                            # 채널의 상세 정보 가져오기
                            details = await get_channel_details(client, chat.id)

                            if details:
                                channel_info = {
                                    'keyword': keyword,
                                    'title': details['channel'].title,
                                    'username': details['channel'].username if hasattr(details['channel'],
                                                                                       'username') else None,
                                    'participants_count': details['participants_count'],
                                    'created_date': details['channel'].date if hasattr(details['channel'],
                                                                                       'date') else None,
                                    'recent_message': details['recent_message'].message if details[
                                        'recent_message'] else None,
                                    'recent_message_date': details['recent_message'].date if details[
                                        'recent_message'] else None,
                                    'about': details['channel'].about if hasattr(details['channel'], 'about') else None
                                }
                                found_channels.append(channel_info)

                                #
                                # # 최근 7일 이내 생성된 채널만 필터링
                                # if channel_info['created_date'] and channel_info['created_date'] > cutoff_time:
                                #     channel_results.append(channel_info)
                        except Exception as detail_error:
                            print(f"채널 세부정보 가져오기 실패: {str(detail_error)}")
                            continue
            results_map[keyword] = found_channels

        except Exception as e:
            print(f"검색 중 오류 발생 (키워드: {keyword}): {str(e)}")
            continue

        # print(results_map)
    display_search_results(results_map)
        #

def display_search_results(results_map):
    """
    Args:
        results_map (dict): 키워드별 채널 검색 결과
                           형식: {'keyword': [channel_info_dict, ...]}
    """
    print("\n\n===== 검색 결과 =====")

    if not results_map:
        print("❌ 검색 결과가 없습니다.")
        return

    for keyword, channels in results_map.items():
        print(f"\n{keyword} 검색중...")

        # 최대 3개만 출력
        channels_to_show = channels[:3]

        if not channels_to_show:
            print(f"❌ {keyword}에 대한 검색 결과가 없습니다.\n---")
            continue

        for i, channel in enumerate(channels_to_show, 1):
            print(f"\n{keyword} [{i}]")
            print(f"📝 채널명: {channel['title']}")
            print(f"👤 아이디: @{channel['username']}" if channel['username'] else "👤 아이디: 비공개")
            print(
                f"👥 참여자: {channel['participants_count']}명" if channel['participants_count'] else "👥 참여자: 정보 없음")

            # 생성일 포맷팅
            if channel['created_date']:
                print(f"📅 생성일: {channel['created_date'].strftime('%Y-%m-%d')}")
            else:
                print("📅 생성일: 정보 없음")

            # 최근 메시지 처리
            if channel['recent_message']:
                # 메시지가 길면 처음 100자만 표시
                message_preview = channel['recent_message'][:100]
                if len(channel['recent_message']) > 100:
                    message_preview += "..."
                print(f"💬 최근 메시지: {message_preview}")

                # 메시지 날짜 처리
                if channel['recent_message_date']:
                    print(f"⏰ 메시지 시간: {channel['recent_message_date'].strftime('%Y-%m-%d %H:%M')}")
                else:
                    print("⏰ 메시지 시간: 정보 없음")
            else:
                print("💬 최근 메시지: 메시지 없음")

            # 채널 설명 처리
            if channel['about']:
                about_preview = channel['about'][:100]
                if len(channel['about']) > 100:
                    about_preview += "..."
                print(f"ℹ️ 설명: {about_preview}")
            else:
                print("ℹ️ 설명: 설명 없음")

            print("---")

        #     # [수정 1] 들여쓰기 수정: 채널 루프 밖으로 이동
        #     # 전체 결과에 추가
        #     # channel_results.extend(found_channels)
        #
        #     # [수정 2] 들여쓰기 수정: 채널 루프 밖으로 이동
        #     # 참여자 수로 정렬 (내림차순)
        #     channel_results.sort(key=lambda x: x['participants_count'] if x['participants_count'] else 0,
        #                          reverse=True)
        #
        #     # [수정 3] 들여쓰기 수정: 채널 루프 밖으로 이동
        #     # [수정 4] 중복 코드 제거: 두 번째 top_3 = channel_results[:3] 제거
        #     top_3 = channel_results[:3]  # 빈 리스트여도 문제없음
        #
        #     # [수정 5] 들여쓰기 수정: 채널 루프 밖으로 이동
        #     if not top_3:
        #         print(f"❌ '{keyword}' 관련 채널을 찾을 수 없습니다.")
        #     else:
        #         for i, channel in enumerate(top_3, 1):
        #             print(f"\n[{i}] {keyword} 검색 결과:")
        #             print("-" * 50)
        #             print(f"📝 채널명: {channel['title']}")
        #             print(f"👤 아이디: @{channel['username']}" if channel['username'] else "👤 아이디: 비공개")
        #             print(f"👥 참여자: {channel['participants_count']}명" if channel[
        #                 'participants_count'] else "👥 참여자: 정보 없음")
        #             print(f"📅 생성일: {channel['created_date'].strftime('%Y-%m-%d')}" if channel[
        #                 'created_date'] else "📅 생성일: 정보 없음")
        #
        #             if channel['recent_message']:
        #                 print(f"💬 최근 메시지: {channel['recent_message'][:50]}" + (
        #                     "..." if len(channel['recent_message']) > 50 else ""))
        #                 print(
        #                     f"⏰ 메시지 시간: {channel['recent_message_date'].strftime('%Y-%m-%d %H:%M') if channel['recent_message_date'] else '정보 없음'}")
        #             else:
        #                 print("💬 최근 메시지: 메시지 없음")
        #
        #             print(f"ℹ️ 설명: {channel['about'][:100]}" + (
        #                 "..." if channel['about'] and len(channel['about']) > 100 else "") if channel[
        #                 'about'] else "ℹ️ 설명: 설명 없음")
        #             print("-" * 50)
        #
        #     # [수정 6] 중복 코드 제거: 여기에 있던 두 번째 top_3 = channel_results[:3] 제거됨
        #
        #
        # except Exception as e:
        #     print(f"검색 중 오류 발생 (키워드: {keyword}): {str(e)}")
        #     continue


async def get_channel_details(client, channel_id):
    """채널의 상세 정보와 최근 메시지를 가져오는 함수"""
    try:
        # 채널의 전체 정보 가져오기
        full_channel = await client.get_entity(channel_id)

        # 최근 메시지 1개 가져오기
        messages = await client.get_messages(channel_id, limit=1)
        recent_message = messages[0] if messages else None

        # 참여자 수 정보 가져오기 (optional)
        try:
            participants_count = None
            if hasattr(full_channel, 'participants_count'):
                participants_count = full_channel.participants_count
            else:
                # 1000명 이하인 경우 실제 참여자 수 확인
                participants = await client.get_participants(channel_id, limit=1000)
                participants_count = len(participants)
        except:
            participants_count = None

        return {
            'channel': full_channel,
            'participants_count': participants_count,
            'recent_message': recent_message
        }
    except Exception as e:
        print(f"채널 세부정보 가져오기 실패: {str(e)}")
        return None