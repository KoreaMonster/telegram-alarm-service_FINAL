# 텔레그램 채널을 검색하여 매일 자동으로 검색하거나, 사용자가 수동으로 채널을 추가할 수 있는 기능을 구현합니다.

import json
import asyncio

from pyexpat.errors import messages

from src.telegram_client import client

channel_names = []  # 채널 목록을 저장하는 리스트 -> 추후 DB로 확장


def load_channel_names(file= 'channel_names.json'):      # 채널 목록을 파일에서 불러오기
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_channel_names(file= "channel_names.json"):      # 채널을 파일에 저장하기
    with open(file, 'w') as f:
        json.dump(channel_names, f)


def add_channel_names(channel_id: str):              #채널을 리스트에 추가하기
    channel_exists = False  #굳이?

    for i in range (len(channel_names)):
        if channel_names[i] == channel_id:
            channel_exists = True
            break
    if channel_exists == False:
        channel_names.append(channel_id)
        save_channel_names()

        print(f"채널 {channel_id}가 추가되었습니다.")
    else:
        print(f"채널 {channel_id}는 이미 존재합니다.")


def remove_channel_names(channel_id: str):            #리스트에 있는 채널을 삭제하기
    channel_exists = False   #굳이?

    for i in range (len(channel_names)):
        if channel_names[i] == channel_id:
            channel_exists = True
            break

    if channel_exists == True:
        channel_names.remove(channel_id)
        save_channel_names()

        print(f"채널 {channel_id}가 삭제되었습니다.")
    else:
        print(f"채널 {channel_id}가 존재하지 않습니다")


def print_channels(file="channel_names.json"):       # 리스트에 있는 채널을 전부 출력하기
    print(f"등록된 Channels: ")

    try:
        with open(file, 'r', encoding='utf-8') as f:
            channels = json.load(f)
            if not channels:
                print("등록된 채널이 없습니다.")
            else:
                for idx, channel in enumerate(channels, start=1):
                    print(f"{idx}. {channel}")
    except FileNotFoundError:
        print(f"'{file}' 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print(f"'{file}' 파일의 형식이 잘못되었습니다.")



async def tel_channel_access():  #메세지 접근 여부 확인
    print(f"등록된 채널 확인\n{load_channel_names()}")

    channel_entity = await client.get_entity(load_channel_names())

    # 단일 채널인 경우 리스트로 감싸기
    if not isinstance(channel_entity, list):
        channel_entity = [channel_entity]

    successful_channels = []

    for channel in channel_entity:
        try:
            print(f"\n🔍 {channel.title} 채널 접근 가능 여부 확인 중...")

            count = 0
            async for message in client.iter_messages(channel, limit=2):
                #print(f"📩 {message.text}")
                count += 1

            if count == 2:
                successful_channels.append(channel)
                print(f"채널 메세지 가져오기 성공")
            else:
                print(f"⚠️ {channel.id}: 메시지 없음")
        except Exception as e:
            print(f"❌ get_messages 오류: {e} ({type(e)})")
    return successful_channels




