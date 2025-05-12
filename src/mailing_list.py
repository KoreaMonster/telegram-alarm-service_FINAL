##메일링 리스트 관리와 등록된 사용자에게 메일을 전송하는 기능

import json


def load_mailing_list(file = "mailing_list.json"):              #json파일 읽기
    try:
        with open(file, 'r') as f:
            mailing_list = json.load(f)
    except FileNotFoundError:
        mailing_list = []

    return mailing_list

def add_email (email, file = "mailing_list.json"):              #json에 메일 추가
    mailing_list = load_mailing_list(file)

    if email not in mailing_list:
        mailing_list.append(email)

        with open(file, 'w') as f:
            json.dump(mailing_list, f, indent=4)

        print(f"{email}이 mailing list에 추가되었습니다.")
    else:
        print(f"{email}은 이미 존재합니다.")


def remove_email (email, file = "mailing_list.json"):           #json에서 메일을 삭제
    mailing_list = load_mailing_list(file)

    if email in mailing_list:
        mailing_list.remove(email)

        with open (file, 'w') as f:
            json.dump(mailing_list, file, indent= 4)
        print(f"{email}이 mailing list에서 삭제되었습니다.")
    else:
        print(f"{email}은 이미 존재하지 않습니다.")

#read email 함수가 필요할까? 일단 나중에 필요하면 추가하ㄱ;