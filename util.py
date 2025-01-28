from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import os

# pandas 이용해서 json파일로 데이터 저장하게 변경

# 1. 처음에 일단 json 읽어오기
# 2. 읽어온걸로 데이터 구성 및 체크 유무에 따른 초기화 알고리즘 실행

# json 정보 구성은?
#     일정 이름, 체크 유무, 마지막 체크 시간, 초기화 알고리즘 종류, 초기화 알고리즘 변수 등

# 메모
# 실시간 저장? (하는 쪽으로 갈 듯?)
# 1회성 일정, 반복 일정?
# 알고리즘 계산에 쓰인 변수에 할당된 메모리 삭제 필요? 자동 삭제되나? 확인 필요...


# json 구성
# ['name', 'checked', 'lastchecktime', 'reset', 'reset_time_input', 'resetparam0']
def load_data(app):
    # json에서 유저 일정 데이터 읽기
    file_path = 'userdata.json'
    if os.path.exists(file_path):
        df = pd.read_json(file_path, orient='records', lines=True)

        # 일정 갯수에 따라 반복문 실행
        for i in range(len(df)):
            todoname = df.iloc[i, 0]
            checked = df.iloc[i, 1]
            lastchecktime = df.iloc[i, 2]
            resetmethod = df.iloc[i, 3]
            resettime = df.iloc[i, 4]
            resetparam0 = df.iloc[i, 5]
            # 체크가 되어있는 경우
            if checked:
                # 체크박스 초기화 알고리즘 실행
                # 0: daily, 1: weekly, 2: monthly
                if resetmethod == 0: checked = daily_reset(resettime, lastchecktime)
                if resetmethod == 1: checked = weekly_reset(resettime, lastchecktime, resetparam0)
                if resetmethod == 2: checked = monthly_reset(resettime, lastchecktime, resetparam0)
                app.add_todo(todoname, checked)

            # 체크가 되어있지 않은 경우
            else:
                app.add_todo(todoname, checked)
            


def save_data(app):
    file_path = 'userdata.json'
    data = [['test name1', 1, '2025-01-27 11:30:21', 0, 300, 0], ['test name2', 1, '2025-01-27 17:30:21', 1, 900, 5], ['test name3', 1, '2025-01-27 17:30:21', 2, 900, 25]]

    df = pd.DataFrame(data, columns=['name', 'checked', 'lastchecktime', 'reset', 'reset_time_input', 'resetparam0'])
    df.to_json(file_path, orient='records', lines=True)


#     1. 시간별(daily), 요일별(weekly), 매 달 ~일 등(monthly)
#         현재 시간 기준으로 초기화 주기에 따른 지난번 초기화 시간을 계산하고, 마지막 체크 시간이 지난번 초기화 시간 이전이라면 체크 해제

#         패러미터 구성
#             daily - 시간 (분) + 마지막 체크 시간, 2개
#             weekly - 요일 + 시간 + 마지막 체크 시간, 3개
#             monthly - 일자 + 시간 + 마지막 체크 시간, 3개

# reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21
def daily_reset(reset_time_input, lastcheck_str): 
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)

    # 현재 시간과 초기화 시간을 비교하여 지난번 초기화 시간 계산
    if now.time() < reset_time: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = 1), reset_time)
    else:
        pre_reset_time = datetime.combine(now.date(), reset_time)

    # 마지막 체크 시간이 지난번 초기화 시간 이전인지 확인
    # 지난번 초기화 시간 이후후면 체크 해제(0), 지난번 초기화 시간 이전이면 체크 유지(1)
    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if lastcheck <= pre_reset_time: 
        return 0
    else:
        return 1

# reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21, weekday : 요일(0-6)
def weekly_reset(reset_time_input, lastcheck_str, weekday):
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)
    weekday = int(weekday)

    # 선택한 요일에서 현재 요일까지의 차이 계산
    days_since_weekday = now.weekday() - weekday + 7
    
    # 다른 요일
    if days_since_weekday < 7: 
        pre_reset_time = datetime.combine(now.date() - timedelta(days = days_since_weekday), reset_time)

    # 같은 요일
    else:
        if now.time() < reset_time: 
            pre_reset_time = datetime.combine(now.date() - timedelta(days = 7), reset_time)
        else:
            pre_reset_time = datetime.combine(now.date(), reset_time)

    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if lastcheck <= pre_reset_time: 
        return 0
    else:
        return 1

# reset_time_input : 분 단위(0-1439), lastcheck_str : %Y-%m-%d %H:%M:%S ex)2025-01-27 11:30:21, reset_day : 일자(1-31)
def monthly_reset(reset_time_input, lastcheck_str, reset_day):
    now = datetime.now()
    reset_time = time(reset_time_input // 60, reset_time_input % 60, 0)
    reset_day= int(reset_day)

    if now.day < reset_day: # 이번달 초기화 일자를 지나지 않은 경우
        pre_reset_time = datetime.combine((now.date() - relativedelta(months = 1)).replace(day = reset_day), reset_time)
    elif now.day == reset_day: # 초기화 당일
        if now.time() < reset_time: 
            pre_reset_time = datetime.combine(now.date() - relativedelta(months = 1), reset_time)
        else:
            pre_reset_time = datetime.combine(now.date(), reset_time)
    else: # 이번달 초기화 일자를 지난 경우
        pre_reset_time = datetime.combine(now.date().replace(day = reset_day), reset_time)

    lastcheck = datetime.strptime(lastcheck_str, '%Y-%m-%d %H:%M:%S')
    if lastcheck <= pre_reset_time: 
        return 0
    else:
        return 1

#     2. 주기별(기준 시간 정하고, 그 시간 기준으로 주기 설정, 초기화시 기준 시간 변경)
#         1. 현재 시간이 기준 시간과 초기화 시간 사이라면 유지.
#         2. 아니라면 초기화 하고 기준 시간을 초기화 시간으로 변경
#         3. 변경된 기준 시간으로 새로운 초기화 시간을 계산하고, 1번으로
        
#         패러미터 구성
#             기준 날짜, 기준 시간, 초기화 주기 + 마지막 체크 시간 4개

#         분 단위로 구현
#         주기별 알고리즘으로 daily weekly 구현도 가능하나, 복잡도상 살짝 손해