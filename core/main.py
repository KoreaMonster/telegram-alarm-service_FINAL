# 메인 프로그램 파일

from app.core.channel_searcher import search_public_channels, get_combined_keyword, add_fixed_keyword, \
    remove_channel_keyword, load_fixed_keyword
from app.core.scraper import recent_10_messages, display_keyword_search_results
from app.core.telegram_client import start_client, client
from app.core.channel_manager import tel_channel_access
from app.core.channel_manager import add_channel_names, remove_channel_names, print_channels

#전역변수
keyword = None              #나중에는 리스트로

async def main():
    #print("클라이언트 실행 중입니다...")
    await start_client()
    #나중에는 회원명 전송하면 그걸로 로그인하기


    print('=' * 50)
    print("🔔 Telegram Keyword Alert Service 시작")

    while True:
        keyword = input("📌 검색할 키워드를 입력하세요: ").strip()
        if keyword:
            break
        else:
            print("키워드는 필수입니다.")

        print(keyword)
    # while True:
    #     target_time_str = input("⏰ 실행 시간을 입력하세요 (기본값: 09:00): ").strip()
    #
    #     if target_time_str:
    #         break
    #     else:
    #         target_time_str = "09:00"
    #
    # os.system('cls')(

    # #Linux
    # #os.system('clear')
    # #print(f"-- 설정값 -- ")
    # print(f"📌 키워드: '{keyword}'")
    # print(f"⏰ 실행 시간: 매일 {target_time_str}")
    print("=" * 50)

    #UserName 관리
    while True:
        print(f"=== Channel ===\n(ex.@test)")
        print(f"1.채널 추가하기\n2.채널 삭제하기\n3.채널목록 출력하기\n4.끝내기\n==============")
        cha = input()


        if cha == '1':
            channel = input().strip()
            add_channel_names(channel)
        elif cha == '2':
            channel = input().strip()
            remove_channel_names(channel)
        elif cha == '3':
            print_channels()
        else:
            break

    successful_channels = await tel_channel_access()
    print(f"\n시작합니다...")
    # await recent_10_messages(successful_channels, keyword)

    # 메시지 검색 실행
    results = await recent_10_messages(successful_channels, keyword)

    # 방법 1: 상세한 결과 출력
    display_keyword_search_results(results, keyword)

    print(f"channel search")
    while True:
        print(f"=== 추천 채널 Keyword ===")
        print(f"1.채널 검색 키워드 추가하기\n2.채널 검색 키워드 삭제하기\n3.채널 검색 키워드 출력하기\n4.끝내기\n==============")
        cha = input()

        if cha == '1':
            channel_keyword = input().strip()
            add_fixed_keyword(channel_keyword)
        elif cha == '2':
            channel_keyword = input().strip()
            remove_channel_keyword(channel_keyword)
        elif cha == '3':
            print(load_fixed_keyword())
        else:
            break


    await search_public_channels(get_combined_keyword())
    # #실제로 실행
    # from src.scraper import start_10_messages
    # await start_10_messages()


    #event 설정해서 새로운 메세지 등장 -> has_keyword -> mailingd
    #await client.run_until_disconnect()

#
# # 클라이언트와 메인 함수 연결
# async def run_client():
#     await client.start()  # 클라이언트 시작
#     await main()  # 메인 함수 실행
#     await client.run_until_disconnected()  # 클라이언트 종료될 때까지 실행
#
# if __name__ == "__main__":
#     # 비동기적으로 클라이언트 실행 및 main() 실행
#     asyncio.run(run_client())

#
# if __name__ == '__main__':
#     asyncio.run(main())

    # loop = asyncio.get_event_loop()
    # try:
    #     loop.run_until_complete(main())
    # except KeyboardInterrupt:
    #     print("종료됨.")
    # finally:
    #     loop.close()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
