from telethon import TelegramClient
from src.config import TELEGRAM_API_ID, TELEGRAM_API_HASH, PHONE_NUMBER, SESSION_NAME

#
# # 세션 이름은 고유하게 설정
# #client = TelegramClient('my_session_1', TELEGRAM_API_ID, TELEGRAM_API_HASH)
#
# client = TelegramClient(
#     'my_session_2',
#     TELEGRAM_API_ID,
#     TELEGRAM_API_HASH,
# )
#
# # 사용자 계정으로 클라이언트 시작
# async def start_client():
#     # 전화번호로 사용자 계정 인증
#     await client.start(phone=PHONE_NUMBER)  # 사용자 전화번호 입력
#     print("사용자 계정으로 로그인 성공")
#
# #client를 불러오는 함수와 생성하는 함수, 삭제하는 함수
#

# 전역 client 객체
client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

async def start_client():
    if not client.is_connected():
        await client.connect()
    if not await client.is_user_authorized():
        phone = PHONE_NUMBER  # 여기에 본인 번호
        await client.send_code_request(phone)
        code = input('Enter the code you received: ')
        await client.sign_in(phone, code)



